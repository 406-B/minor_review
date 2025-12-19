#!/bin/bash

# Docker启动脚本
# 用于快速启动本地开发环境

set -e

echo "🐳 启动小众点评本地开发环境..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装，请先安装Docker"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose未安装，请先安装docker-compose"
        exit 1
    fi
}

# 停止并清理现有的容器
cleanup() {
    print_info "清理现有的容器..."
    docker-compose down -v 2>/dev/null || true
}

# 启动服务
start_services() {
    local mode=${1:-dev}

    if [ "$mode" = "prod" ]; then
        print_info "启动生产环境模式..."
        docker-compose --profile prod up --build
    else
        print_info "启动开发环境模式..."
        docker-compose up --build
    fi
}

# 显示服务状态
show_status() {
    print_info "服务状态："
    echo ""
    echo "📊 数据库 (PostgreSQL): http://localhost:5432"
    echo "🔄 Redis缓存: http://localhost:6379"
    echo "🖥️  后端API: http://localhost:8000"
    echo "🌐 前端应用: http://localhost:3000"
    echo "🔗 Nginx代理: http://localhost:80"
    echo ""
    echo "📝 API文档: http://localhost:8000/api/docs/"
    echo "🗄️  管理后台: http://localhost:8000/admin/"
    echo ""
}

# 初始化数据库
init_database() {
    print_info "等待数据库启动..."
    sleep 10

    print_info "运行数据库迁移..."
    docker-compose exec backend python manage.py migrate

    print_info "创建超级用户..."
    docker-compose exec backend python manage.py createsuperuser --noinput \
        --username admin \
        --email admin@example.com || true

    print_info "加载初始数据..."
    # 如果有fixture文件，可以在这里加载
    # docker-compose exec backend python manage.py loaddata fixtures.json || true
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  start       启动开发环境 (默认)"
    echo "  start-prod  启动生产环境"
    echo "  stop        停止所有服务"
    echo "  restart     重启服务"
    echo "  logs        查看日志"
    echo "  status      显示服务状态"
    echo "  init-db     初始化数据库"
    echo "  clean       清理所有容器和数据卷"
    echo "  help        显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start      # 启动开发环境"
    echo "  $0 start-prod # 启动生产环境"
    echo "  $0 logs -f    # 查看实时日志"
}

# 主函数
main() {
    local command=${1:-start}

    case $command in
        start)
            check_docker
            cleanup
            start_services dev
            ;;
        start-prod)
            check_docker
            cleanup
            start_services prod
            ;;
        stop)
            print_info "停止服务..."
            docker-compose down
            print_success "服务已停止"
            ;;
        restart)
            print_info "重启服务..."
            docker-compose restart
            print_success "服务已重启"
            ;;
        logs)
            shift
            docker-compose logs "$@"
            ;;
        status)
            show_status
            echo ""
            docker-compose ps
            ;;
        init-db)
            init_database
            ;;
        clean)
            print_warning "这将删除所有容器、镜像和数据卷！"
            read -p "确定要继续吗? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                print_info "清理所有Docker资源..."
                docker-compose down -v --rmi all
                docker system prune -f
                print_success "清理完成"
            fi
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "未知命令: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 检查参数
if [ $# -eq 0 ]; then
    # 默认启动开发环境
    main start
else
    main "$@"
fi
