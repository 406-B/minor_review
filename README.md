# Minor Review Project

Software engineering project with code quality tools configured.

## Code Quality Tools

This project is configured with:

- **Prettier**: Code formatter for consistent code style
- **ESLint**: JavaScript/TypeScript linter for code quality
- **EditorConfig**: Maintains consistent coding styles across different editors
- **Jest**: JavaScript testing framework for unit tests
- **Cypress**: End-to-end testing framework for browser testing
- **Apifox**: API documentation and testing tool

## Installation

Install the dependencies:

```bash
npm install
```

Or if you use yarn:

```bash
yarn install
```

Or if you use pnpm:

```bash
pnpm install
```

## Usage

### Format Code

Format all supported files:

```bash
npm run format
```

Check if files are formatted correctly (without modifying):

```bash
npm run format:check
```

### Lint Code

Lint JavaScript/TypeScript files:

```bash
npm run lint
```

Auto-fix linting issues:

```bash
npm run lint:fix
```

### Run Tests

Run Jest unit tests:

```bash
npm run test
```

Run tests in watch mode (re-runs on file changes):

```bash
npm run test:watch
```

Run tests with coverage report:

```bash
npm run test:coverage
```

### Cypress E2E Tests

Open Cypress Test Runner (interactive mode):

```bash
npm run cypress:open
```

Run Cypress tests headlessly:

```bash
npm run cypress:run
```

## Configuration

### Jest

Configuration: `package.json` (jest field)

Settings:

- Test environment: Node.js
- Coverage directory: `coverage/`
- Test file patterns: `**/*.test.js`, `**/*.spec.js`
- Supported extensions: js, jsx, ts, tsx, json

### Cypress

Configuration file: `cypress.config.js`

Settings:

- Base URL: http://localhost:3000
- Test files: `cypress/e2e/**/*.cy.{js,jsx,ts,tsx}`
- Viewport: 1280x720
- Videos and screenshots enabled

Directory structure:

```
cypress/
├── e2e/          # End-to-end tests
├── fixtures/      # Test data files
├── support/       # Custom commands and helpers
└── downloads/     # Downloaded files (git-ignored)
```

### Prettier

Configuration file: `.prettierrc`

Key settings:

- Single quotes
- Semicolons enabled
- 2 spaces indentation
- 100 characters line width
- Trailing commas in ES5-compatible locations

Ignored files: `.prettierignore`

### ESLint

Configuration file: `.eslintrc.json`

Features:

- TypeScript support
- Prettier integration
- Recommended rules from ESLint and TypeScript
- Warns on console statements
- Warns on unused variables (except those starting with `_`)

Ignored files: `.eslintignore`

### EditorConfig

Configuration file: `.editorconfig`

Ensures consistent formatting across different programming languages:

- JavaScript/TypeScript: 2 spaces
- Python/Java/C++: 4 spaces
- Go: tabs
- UTF-8 encoding
- LF line endings

## IDE Integration

### VS Code

Install these extensions:

- ESLint
- Prettier - Code formatter
- EditorConfig for VS Code

Add to `.vscode/settings.json`:

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

### WebStorm / IntelliJ IDEA

1. Go to Settings → Languages & Frameworks → JavaScript → Prettier
2. Enable "On save" and "On Reformat Code"
3. Go to Settings → Languages & Frameworks → JavaScript → Code Quality Tools → ESLint
4. Enable "Automatic ESLint configuration"

## API Documentation

This project uses Apifox to maintain API documentation. The OpenAPI specification is stored in `docs/api/openapi.json`.

### Setting Up Apifox

1. **Install Apifox**: Download from [https://apifox.com](https://apifox.com)
2. **Import Project**:
   - Open Apifox
   - Click "Import" → "OpenAPI"
   - Select `docs/api/openapi.json`
3. **Configure Environment**:
   - Edit `.apifoxrc.json` with your environment variables
   - Or set up environments directly in Apifox UI

### Using Apifox

#### Import API Documentation

```bash
# In Apifox, import the OpenAPI specification
# File → Import → OpenAPI/Swagger → Select docs/api/openapi.json
```

#### Export Changes

When you make changes in Apifox:

1. In Apifox: Settings → Export → OpenAPI 3.0
2. Save as `docs/api/openapi.json`
3. Commit to Git

#### Update from Code

When you update the API specification file:

1. Edit `docs/api/openapi.json`
2. In Apifox: Settings → Import → Replace with file
3. Select the updated `docs/api/openapi.json`

### API Documentation Structure

```
docs/api/
├── README.md       # How to use Apifox with this project
└── openapi.json    # OpenAPI 3.0 specification
```

### Example API Endpoints

The project includes example API endpoints:

- `POST /auth/login` - User authentication
- `POST /auth/logout` - User logout
- `GET /users` - List all users
- `GET /users/{id}` - Get user by ID
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user

For detailed usage instructions, see [`docs/api/README.md`](docs/api/README.md).

### Environment Variables

Configure environments in `.apifoxrc.json`:

- **Development**: http://localhost:3000/api
- **Staging**: https://staging-api.example.com
- **Production**: https://api.example.com
