import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from list.models import Canteen, Dish, Floor, Tag, Window


DEFAULT_TAGS = [
    "Spicy",
    "Vegetarian",
    "Sweet",
    "Gluten-Free",
    "Popular",
    "Hot",
    "Cold",
    "Noodles",
    "Rice",
    "Soup",
]


def _rand_price(rng: random.Random) -> Decimal:
    # 2.00 ~ 25.00
    return Decimal(rng.randint(200, 2500)) / Decimal(100)


class Command(BaseCommand):
    help = "Seed load-test data for list app (canteens/tags/dishes)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=200,
            help="Number of dishes to create (default: 200)",
        )
        parser.add_argument(
            "--canteens",
            type=int,
            default=5,
            help="Number of canteens to ensure (default: 5)",
        )
        parser.add_argument(
            "--tags",
            type=int,
            default=10,
            help="Number of tags to ensure (default: 10)",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=20250101,
            help="Random seed for deterministic data (default: 20250101)",
        )
        parser.add_argument(
            "--truncate",
            action="store_true",
            help="Delete existing seeded records before creating new ones",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=200,
            help="Bulk create batch size (default: 200)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        count: int = options["count"]
        canteens_n: int = options["canteens"]
        tags_n: int = options["tags"]
        seed: int = options["seed"]
        truncate: bool = options["truncate"]
        batch_size: int = options["batch_size"]

        if count <= 0:
            self.stdout.write(self.style.WARNING("Nothing to do: --count <= 0"))
            return
        if canteens_n <= 0:
            raise ValueError("--canteens must be > 0")
        if tags_n <= 0:
            raise ValueError("--tags must be > 0")
        if batch_size <= 0:
            raise ValueError("--batch-size must be > 0")

        rng = random.Random(seed)

        if truncate:
            # Keep it simple and explicit: only delete list app data.
            # Clear M2M first to avoid FK constraint surprises.
            Dish.tags.through.objects.all().delete()
            Dish.pending_tags.through.objects.all().delete()
            Dish.objects.all().delete()
            Window.objects.all().delete()
            Floor.objects.all().delete()
            Canteen.objects.all().delete()
            Tag.objects.all().delete()
            self.stdout.write(self.style.WARNING("Truncated list app data"))

        # 1) Ensure canteens
        existing_canteens = list(Canteen.objects.order_by("id"))
        need_canteens = max(0, canteens_n - len(existing_canteens))
        if need_canteens > 0:
            Canteen.objects.bulk_create(
                [
                    Canteen(
                        name=f"LoadTest Canteen {i + 1}",
                        latitude=None,
                        longitude=None,
                        address=f"LoadTest Address {i + 1}",
                    )
                    for i in range(need_canteens)
                ],
                batch_size=batch_size,
            )
        canteens = list(Canteen.objects.order_by("id")[:canteens_n])

        # 2) Ensure floors/windows for each canteen (for nicer UI + window FK options)
        for canteen in canteens:
            if not Floor.objects.filter(canteen=canteen).exists():
                floors = [
                    Floor(name="1F", canteen=canteen, order=1),
                    Floor(name="2F", canteen=canteen, order=2),
                ]
                Floor.objects.bulk_create(floors, batch_size=batch_size)

            floors = list(Floor.objects.filter(canteen=canteen).order_by("order", "id"))
            for floor in floors:
                if not Window.objects.filter(floor=floor).exists():
                    windows = [
                        Window(name="A", floor=floor, order=1),
                        Window(name="B", floor=floor, order=2),
                        Window(name="C", floor=floor, order=3),
                    ]
                    Window.objects.bulk_create(windows, batch_size=batch_size)

        all_windows = list(Window.objects.select_related("floor", "floor__canteen"))
        if not all_windows:
            # This should not happen, but keep it robust.
            self.stdout.write(self.style.WARNING("No windows found; dishes will have window=NULL"))

        # 3) Ensure tags
        desired_names = list(dict.fromkeys(DEFAULT_TAGS))
        while len(desired_names) < tags_n:
            desired_names.append(f"Tag{len(desired_names) + 1}")
        desired_names = desired_names[:tags_n]

        existing_tag_names = set(Tag.objects.values_list("name", flat=True))
        to_create = [Tag(name=n) for n in desired_names if n not in existing_tag_names]
        if to_create:
            Tag.objects.bulk_create(to_create, batch_size=batch_size)
        tags = list(Tag.objects.filter(name__in=desired_names).order_by("id"))

        # 4) Create dishes
        new_dishes = []
        for i in range(count):
            canteen = rng.choice(canteens)
            window = rng.choice(all_windows) if all_windows and rng.random() < 0.85 else None
            name = f"LoadTest Dish {canteen.id}-{i + 1:05d}"
            new_dishes.append(
                Dish(
                    name=name,
                    description="Seeded for load testing",
                    price=_rand_price(rng),
                    canteen=canteen,
                    window=window,
                    rating=Decimal("0.0"),
                    rating_count=0,
                    view_count=0,
                )
            )

        # NOTE: MySQL doesn't reliably return auto-generated PKs for bulk_create
        # across all Django/MySQLdb combos, so we can't depend on dish.id here.
        # We'll create dishes in bulk, then re-query and attach tags via ORM.
        Dish.objects.bulk_create(new_dishes, batch_size=batch_size)

        created = list(
            Dish.objects.filter(name__startswith="LoadTest Dish ")
            .order_by("-id")[:count]
        )

        # 5) Attach tags.
        # Each dish gets 0-3 tags, skewed to 1.
        if tags:
            for dish in created:
                k = rng.choices([0, 1, 2, 3], weights=[10, 55, 25, 10], k=1)[0]
                if k <= 0:
                    continue
                dish.tags.set(rng.sample(tags, k=min(k, len(tags))))

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded: canteens={len(canteens)} windows={len(all_windows)} tags={len(tags)} dishes_created={len(created)}"
            )
        )
