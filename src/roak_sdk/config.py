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
    "Rotation Pressure",
    "Torque",
]
DEFAULT_RIG_FEEDS = DEFAULT_BOREHOLE_FEEDS # Rigs have the same feeds as boreholes

# -- Type lists --- 

RIG_TYPES = [ 'MWD_CRS_S', 'MWD_MRS_XL_275_MAX_DUO', 'MWD_MRS_XL_275_MAX',
              'MWD_CRS_XL_170_DUO', 'MWD_CRS_XL_170', 'MWD_MRS_200', 'MWD_MRS_200_DUO',
             'MWD_CRS_XL_140_DUO', 'MWD_CRS_XL_140', 'MWD_SRS_ML_DUO', 'MWD_SRS_ML',]

ALL_ASSET_TYPES = ['Media folder', 'Site', 'Project', 'Customer root',
                   'Modem on well', 'Modems', 'GWM Well', 'Rig on site', 
                   'Borehole', 'Rigs', 'Lysimeter', 'SDI-12', 'Modem logger',
                   'GPS Logger', 'Internal barometer', 'CTD-Diver 17',
                   'CTD-Diver', 'Cera-Diver', 'Micro-Diver', 'Mini-Diver',
                   'TD-Diver', 'GDT-S Prime pulse', 'GDT-S Prime plus', 
                   'GDT-S Prime', 'GDT-S', 'GDT-M', 'CRS-S', 'MRS XL 275 MAX DUO',
                   'MRS XL 275 MAX', 'CRS XL 170 DUO', 'CRS XL 170',
                   'CRS XL 140 DUO', 'CRS XL 140', 'SRS ML DUO', 'SRS ML', 
                   'prediction_cable', 'prediction_diver', 'Cable prediction', 
                   'Tenant properties', 'Test_ANT_Same_name', 'Prime Pro 300', 
                   'Prime Pro 300 V0', 'Prime Pro 400', 'MRS 200', 'MRS 200 DUO', 
                   'CTD-Diver 24', 'RFID_Tool_Data_Test', 'test', 'gene',
                   'Data Sources', 'Data Source', 'Generic Asset', 'SDI12_GUID',
                   'Test-Device-Type', 'HYDRAPROBE',
                   'LEVELLINE', 'SCUBA', 'STS', 'testdevice', 'Scuba_16']