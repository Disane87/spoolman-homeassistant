"""Constants for the spoolman integration."""

DOMAIN = "spoolman"
DEFAULT_NAME = "Spoolman"
SPOOLMAN_INFO_PROPERTY = "spoolman_info"

CONF_URL = "spoolman_url"
CONF_SHOW_ARCHIVED = "show_archived"
CONF_UPDATE_INTERVAL = "update-interval"
CONF_NOTIFICATION_THRESHOLD_INFO = "notification_threshold_info"
CONF_NOTIFICATION_THRESHOLD_WARNING = "notification_threshold_warning"
CONF_NOTIFICATION_THRESHOLD_CRITICAL = "notification_threshold_critical"

PUBLIC_IMAGE_PATH = "www/spoolman_images"
LOCAL_IMAGE_PATH = "/local/spoolman_images"

EVENT_THRESHOLD_EXCEEDED = "spoolman_spool_threshold_exceeded"

NOTIFICATION_THRESHOLDS = {"critical": 95, "warning": 75, "info": 50}
SPOOLMAN_API_WRAPPER = "spoolman_api_wrapper"

KLIPPER_URL = "klipper_url"
KLIPPER_URL_DESC = "klipper_url_desc"
