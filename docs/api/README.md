# API Documentation

This directory contains API documentation files that can be imported into Apifox.

## Files

- `openapi.json` - OpenAPI 3.0 specification file
- `apifox-export.md` - Apifox export instructions

## Usage with Apifox

### Importing API Documentation

1. **Open Apifox**
2. **Import Project**:
   - Click "Import" → "OpenAPI"
   - Select `docs/api/openapi.json`
3. **Verify Import**: Check that all endpoints are imported correctly

### Synchronizing Changes

When you update the API documentation:

1. Edit `openapi.json` file
2. In Apifox, go to "Settings" → "Import"
3. Choose "Replace with file" and select the updated `openapi.json`

### Exporting from Apifox

To export changes made in Apifox back to the repository:

1. In Apifox, click "Settings" → "Export"
2. Choose "OpenAPI 3.0" format
3. Save as `docs/api/openapi.json` (replace the existing file)
4. Commit the changes to Git

## Maintaining API Documentation

### Adding New Endpoints

1. Update `docs/api/openapi.json`:
   - Add new path under `paths`
   - Add request/response schemas in `components.schemas`
   - Add security requirements if needed

2. Import to Apifox:
   - Use the import feature to sync changes

### API Versioning

- Major versions should be reflected in the base URL
- Update the `servers` array for new API versions
- Keep backward compatibility documentation

### Schema Reuse

- Use `$ref` to reference reusable schemas
- Common schemas are defined in `components.schemas`
- Common responses are defined in `components.responses`

## Best Practices

1. **Keep documentation up to date**: Update API docs when code changes
2. **Use descriptive examples**: Provide realistic example values
3. **Document all parameters**: Include required vs optional parameters
4. **Add error responses**: Document all possible error scenarios
5. **Use consistent naming**: Follow RESTful conventions
6. **Version control**: Commit API documentation changes with code changes
