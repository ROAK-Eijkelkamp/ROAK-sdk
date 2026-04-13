"""
Configuration constants for the ROAK SDK.
"""

# --- API URLs ---
DEFAULT_BASE_URL = "https://royaleijkelkamp.roak.com"

# --- API Endpoints (relative paths) ---
AUTH_EMAIL_ENDPOINT = "/api/ed/authentication/email"
AUTH_REFRESH_ENDPOINT = "/api/ed/authentication/renewal"

# --- Time Constants ---
MILLISECONDS_IN_ONE_DAY = 86400000

# --- Request Settings ---
DEFAULT_REQUEST_TIMEOUT = 30  # seconds
DEFAULT_HTTP_RETRY_ATTEMPTS = 3
DEFAULT_HTTP_RETRY_BACKOFF_FACTOR = 0.5
DEFAULT_HTTP_RETRY_STATUS_CODES = (429, 500, 502, 503, 504)


def normalize_request_timeout(timeout: int | float | None) -> float | None:
    """Normalize request timeout input.

    None or negative values disable request timeouts.
    """
    if timeout is None:
        return None
    if timeout < 0:
        return None
    return float(timeout)

# --- Asset Types ---
CUSTOMER_TYPE = 'ED_CUSTOMER_ROOT'
ASSET_TYPES = ['GWM_WELL', 'MWD_BOREHOLE']
ASSET_TYPE_LIST = ['ED_SITE', 'GWM_WELL', 'MWD_BOREHOLE', 'ED_SITE']
MODEM_TYPES = ['GWM_SDI_12', 'GWM_GDT_S_PRIME_PULSE', 'GWM_GDT_S_PRIME_PLUS', 'GWM_GDT_S_PRIME', 'GWM_GDT_S', 'GWM_GDT_M', 'GWM_GDT_PRO_300', 'GWM_GDT_PRO_400']

# --- Default Feeds ---
DEFAULT_WELL_FEEDS = [
    "waterLevelReference",
]

DEFAULT_BOREHOLE_FEEDS = [
    "Pulldown Pressure",
    "Pullup Pressure",

    "Flushing Pressure",
    "Flushing Debit",

    "Torque",
    "Rotation Speed",

    "Penetration Speed",

    "Sonic Speed",
    "Sonic Frequency"
]

DEFAULT_RIG_FEEDS = DEFAULT_BOREHOLE_FEEDS # Rigs have the same feeds as boreholes

# -- Type lists --- 

RIG_TYPES = [ 'MWD_CRS_S', 'MWD_MRS_XL_275_MAX_DUO', 'MWD_MRS_XL_275_MAX',
              'MWD_CRS_XL_170_DUO', 'MWD_CRS_XL_170', 'MWD_MRS_200', 'MWD_MRS_200_DUO',
              'MWD_CRS_XL_140_DUO', 'MWD_CRS_XL_140', 'MWD_SRS_ML_DUO', 'MWD_SRS_ML',
              'Reichdrill', 'Fraste FS250', 'GTD35']