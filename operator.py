
import kopf
from healthchecks_io import AsyncClient, CheckCreate, HCAPIAuthError, HCAPIError, CheckNotFoundError, BadAPIRequestError, HCAPIRateLimitError
import os
from dataclasses import dataclass

@dataclass
class Config:
    healthchecks_url: str
    healthchecks_api_key: str

NAMESPACE = ('healthchecks.io', 'check')
CONFIG: Config

@kopf.on.startup()
async def startup_fn(logger, **kwargs) -> None:
    global CONFIG
    hc_url = os.environ.get("HEALTHCHECKS_URL", "https://healthchecks.io/api/")
    hc_api_key = os.environ.get("HEALTHCHECKS_API_KEY", None)
    if hc_api_key is None:
        raise kopf.PermanentError("No HEALTHCHECKS_API_KEY environment variable found")
    CONFIG = Config(healthchecks_url=hc_url, healthchecks_api_key=hc_api_key)

@kopf.on.create(*NAMESPACE)
async def create_fn(body, logger, patch, **kwargs):
    if 'channels' in body['spec']:
        body['spec']['channels'] = ",".join(body['spec']['channels'])
    if 'tags' in body['spec']:
        body['spec']['tags'] = ",".join(body['spec']['tags'])
    if 'unique' in body['spec']:
        body['spec']['unique'] = ",".join(body['spec']['unique'])

    try:
        new_check = CheckCreate(
            name=body['metadata']['name'], **body['spec'])
    except Exception as exc:
        raise kopf.PermanentError(f"Error while validating new check {exc}")
    try:
        async with AsyncClient(api_key=CONFIG.healthchecks_api_key, api_url=CONFIG.healthchecks_url) as client:
            check = await client.create_check(new_check)
    except HCAPIRateLimitError as exc:
        raise kopf.TemporaryError("Rate limit error from the hc api", delay=60)
    except HCAPIAuthError:
        raise kopf.PermanentError("API Auth Error")
    except BadAPIRequestError as exc:
        raise kopf.PermanentError(f"Error when posting to the HC api {exc}")
    for key, val in check.dict().items():
        patch.status[key] = val
    return "Success"

@kopf.on.delete(*NAMESPACE)
async def delete_fn(name, logger, body, **kwargs):
    logger.debug("Deleting check %s - %s", name, body['status']['uuid'] )
    
    try:
        async with AsyncClient(api_key=CONFIG.healthchecks_api_key, api_url=CONFIG.healthchecks_url) as client:
            check = await client.delete_check(body['status']['uuid'])
    except HCAPIRateLimitError as exc:
        raise kopf.TemporaryError("Rate limit error from the hc api", delay=60)
    except HCAPIAuthError:
        raise kopf.PermanentError("API Auth Error")
    except BadAPIRequestError as exc:
        raise kopf.PermanentError(f"Error when posting to the HC api {exc}")
    return {"deleted": True}

@kopf.on.update(*NAMESPACE)
async def update_fn(name, spec, status, body, logger, **kwargs):
    logger.debug("Updating check %s - %s", name, spec )
    if 'channels' in spec:
        spec['channels'] = ",".join(spec['channels'])
    if 'tags' in spec:
        spec['tags'] = ",".join(spec['tags'])
    if 'unique' in spec:
        spec['unique'] = ",".join(spec['unique'])

    try:
        new_check = CheckCreate(
            name=body['metadata']['name'], **spec)
    except Exception as exc:
        raise kopf.PermanentError(f"Error while validating new check {exc}")
    
    try:
        async with AsyncClient(api_key=CONFIG.healthchecks_api_key, api_url=CONFIG.healthchecks_url) as client:
            check = await client.update_check(body['status']['uuid'], new_check)
    except HCAPIRateLimitError as exc:
        raise kopf.TemporaryError("Rate limit error from the hc api", delay=60)
    except HCAPIAuthError:
        raise kopf.PermanentError("API Auth Error")
    except BadAPIRequestError as exc:
        raise kopf.PermanentError(f"Error when posting to the HC api {exc}")
    return {"updated": True}
