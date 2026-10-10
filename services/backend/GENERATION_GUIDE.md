# AI Studio Backend - Generation Integration Tests

## Running Tests

```bash
cd services/backend
python -m pytest tests/
```

## Test Coverage

- **Hardware Detection**: CPU cores, RAM, storage, GPU/VRAM detection
- **Resource Profiles**: Low Resource, Balanced, Quality mode defaults
- **Generation Validation**: Prompt validation, resolution limits, parameter ranges
- **ComfyUI Integration**: Workflow building, model detection, requirements checking
- **Coordination**: Pre-flight checks before generation, hardware-software compatibility
- **Database**: Project creation, generation history logging

## Generation Flow

1. **Request Validation**: `/generate/validate` - Check parameters
2. **Pre-flight Check**: `/generation/can-proceed` - Verify hardware, ComfyUI, models
3. **Job Creation**: `/generate` - Queue the generation
4. **Queue Processing**: Background worker processes the job
5. **Output**: Save to disk, log to database, return file path

## Low-Resource Support

The backend automatically:
- Detects available RAM, CPU cores, and VRAM
- Adjusts resolution and steps for low-resource systems
- Falls back to CPU if GPU is unavailable
- Provides explicit warnings about unsupported configurations
- Never fakes generation output (except placeholder for testing)
