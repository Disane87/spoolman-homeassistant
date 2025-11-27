"""Spoolman home assistant sensor platform."""

import logging
import os

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from PIL import Image, ImageDraw

from .const import (
    DEFAULT_SPOOL_COLOR_HEX,
    DOMAIN,
    LOCAL_IMAGE_PATH,
    PUBLIC_IMAGE_PATH,
)
from .sensors import (
    Filament,
    FilamentArticleNumber,
    FilamentBedTemp,
    FilamentColorHex,
    FilamentDensity,
    FilamentDiameter,
    FilamentExtruderTemp,
    FilamentMaterial,
    FilamentName,
    FilamentWeight,
    Spool,
    SpoolComment,
    SpoolEstimatedRunOut,
    SpoolFirstUsed,
    SpoolFlowRate,
    SpoolId,
    SpoolLastUsed,
    SpoolLocation,
    SpoolLotNumber,
    SpoolPrice,
    SpoolRegistered,
    SpoolRemainingLength,
    SpoolUsedLength,
    SpoolUsedPercentage,
    SpoolUsedWeight,
    SpoolWeight,
    VendorName,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up Spoolman sensors from a config entry."""
    # Use the coordinator from hass.data that was created in __init__.py
    coordinator = hass.data[DOMAIN]["coordinator"]

    if coordinator.data:
        all_entities = []
        image_dir = hass.config.path(PUBLIC_IMAGE_PATH)

        # Create spool entities
        spool_data = coordinator.data.get("spools", [])
        for idx, spool in enumerate(spool_data):
            image_url = await hass.async_add_executor_job(
                _generate_entity_picture, spool, image_dir
            )
            spool_device = Spool(
                hass, coordinator, spool, idx, config_entry, image_url
            )
            all_entities.append(spool_device)

            # Create flow rate sensor for this spool
            flow_rate_sensor = SpoolFlowRate(
                hass, coordinator, spool, config_entry
            )
            all_entities.append(flow_rate_sensor)

            # Create estimated run out sensor for this spool
            estimated_runout_sensor = SpoolEstimatedRunOut(
                hass, coordinator, spool, config_entry
            )
            all_entities.append(estimated_runout_sensor)

            # Create additional sensors to reduce state attributes (#71)
            # Used weight sensor
            used_weight_sensor = SpoolUsedWeight(
                hass, coordinator, spool, config_entry
            )
            all_entities.append(used_weight_sensor)

            # Remaining length sensor
            remaining_length_sensor = SpoolRemainingLength(
                hass, coordinator, spool, config_entry
            )
            all_entities.append(remaining_length_sensor)

            # Used length sensor
            used_length_sensor = SpoolUsedLength(
                hass, coordinator, spool, config_entry
            )
            all_entities.append(used_length_sensor)

            # Location sensor (text)
            location_sensor = SpoolLocation(
                hass, coordinator, spool, config_entry
            )
            all_entities.append(location_sensor)

            # Used percentage sensor
            used_percentage_sensor = SpoolUsedPercentage(
                hass, coordinator, spool, config_entry
            )
            all_entities.append(used_percentage_sensor)

            # Metadata sensors (rarely changing)
            # Registered timestamp
            if spool.get("registered"):
                registered_sensor = SpoolRegistered(
                    hass, coordinator, spool, config_entry
                )
                all_entities.append(registered_sensor)

            # First used timestamp
            if spool.get("first_used"):
                first_used_sensor = SpoolFirstUsed(
                    hass, coordinator, spool, config_entry
                )
                all_entities.append(first_used_sensor)

            # Last used timestamp
            if spool.get("last_used"):
                last_used_sensor = SpoolLastUsed(
                    hass, coordinator, spool, config_entry
                )
                all_entities.append(last_used_sensor)

            # Price sensor
            if spool.get("price") is not None:
                price_sensor = SpoolPrice(
                    hass, coordinator, spool, config_entry
                )
                all_entities.append(price_sensor)

            # Spool weight (tare weight)
            if spool.get("spool_weight") is not None:
                spool_weight_sensor = SpoolWeight(
                    hass, coordinator, spool, config_entry
                )
                all_entities.append(spool_weight_sensor)

            # Lot number
            if spool.get("lot_nr"):
                lot_nr_sensor = SpoolLotNumber(
                    hass, coordinator, spool, config_entry
                )
                all_entities.append(lot_nr_sensor)

            # Comment
            if spool.get("comment"):
                comment_sensor = SpoolComment(
                    hass, coordinator, spool, config_entry
                )
                all_entities.append(comment_sensor)

            # Filament properties sensors
            filament = spool.get("filament", {})

            # Density
            if filament.get("density") is not None:
                density_sensor = FilamentDensity(
                    hass, coordinator, spool, config_entry
                )
                all_entities.append(density_sensor)

            # Diameter
            if filament.get("diameter") is not None:
                diameter_sensor = FilamentDiameter(
                    hass, coordinator, spool, config_entry
                )
                all_entities.append(diameter_sensor)

            # Extruder temperature
            if filament.get("settings_extruder_temp") is not None:
                extruder_temp_sensor = FilamentExtruderTemp(
                    hass, coordinator, spool, config_entry
                )
                all_entities.append(extruder_temp_sensor)

            # Bed temperature
            if filament.get("settings_bed_temp") is not None:
                bed_temp_sensor = FilamentBedTemp(
                    hass, coordinator, spool, config_entry
                )
                all_entities.append(bed_temp_sensor)

            # Article number
            if filament.get("article_number"):
                article_number_sensor = FilamentArticleNumber(
                    hass, coordinator, spool, config_entry
                )
                all_entities.append(article_number_sensor)


            # Basic attribute sensors (always create for compatibility)
            # ID sensor
            id_sensor = SpoolId(
                hass, coordinator, spool, config_entry
            )
            all_entities.append(id_sensor)

            # Filament name
            if filament.get("name"):
                filament_name_sensor = FilamentName(
                    hass, coordinator, spool, config_entry
                )
                all_entities.append(filament_name_sensor)

            # Filament material
            if filament.get("material"):
                material_sensor = FilamentMaterial(
                    hass, coordinator, spool, config_entry
                )
                all_entities.append(material_sensor)

            # Filament color hex
            if filament.get("color_hex"):
                # Generate entity picture for color visualization
                image_url = await hass.async_add_executor_job(
                    _generate_filament_entity_picture, filament, image_dir
                )
                color_hex_sensor = FilamentColorHex(
                    hass, coordinator, spool, config_entry, image_url
                )
                all_entities.append(color_hex_sensor)

            # Vendor name
            if filament.get("vendor", {}).get("name"):
                vendor_sensor = VendorName(
                    hass, coordinator, spool, config_entry
                )
                all_entities.append(vendor_sensor)

            # Filament weight (initial/total)
            if filament.get("weight") is not None:
                filament_weight_sensor = FilamentWeight(
                    hass, coordinator, spool, config_entry
                )
                all_entities.append(filament_weight_sensor)

        # Create filament entities
        filament_data = coordinator.data.get("filaments", [])
        for idx, filament in enumerate(filament_data):
            image_url = await hass.async_add_executor_job(
                _generate_filament_entity_picture, filament, image_dir
            )
            filament_device = Filament(
                hass, coordinator, filament, idx, config_entry, image_url
            )
            all_entities.append(filament_device)

        async_add_entities(all_entities)


def _generate_entity_picture(spool_data, image_dir):
    """Generate an entity picture with the specified color(s) and save it to the www directory."""
    filament = spool_data.get("filament", {})

    # Retrieve color(s)
    multi_color_hexes = filament.get("multi_color_hexes", "").split(",")
    color_hex = filament.get("color_hex", DEFAULT_SPOOL_COLOR_HEX)
    multi_color_direction = filament.get("multi_color_direction", "coaxial")

    # Determine colors: prioritize multi_color_hexes if available
    if multi_color_hexes and any(c.strip() for c in multi_color_hexes):
        colors = [c.strip() for c in multi_color_hexes if len(c.strip()) == 6]
    elif color_hex:
        colors = [color_hex]
    else:
        _LOGGER.warning(
            "SpoolManCoordinator: Spool with ID '%s' has no valid color information.",
            spool_data.get("id", "unknown"),
        )
        return None

    # Create image
    image_size = (100, 100)
    image = Image.new("RGB", image_size, int(DEFAULT_SPOOL_COLOR_HEX, 16))
    draw = ImageDraw.Draw(image)

    # Draw colors
    if len(colors) > 1:
        if multi_color_direction == "coaxial":
            step = image_size[0] // len(colors)
            for i, color in enumerate(colors):
                draw.rectangle([
                    (i * step, 0),
                    ((i + 1) * step - 1, image_size[1])
                ], fill=f"#{color}")
        elif multi_color_direction == "longitudinal":
            step = image_size[1] // len(colors)
            for i, color in enumerate(colors):
                draw.rectangle([
                    (0, i * step),
                    (image_size[0], (i + 1) * step - 1)
                ], fill=f"#{color}")
    else:
        # Single color fallback
        draw.rectangle([(0, 0), image_size], fill=f"#{colors[0]}")

    # Save the image
    image_name = f"spool_{spool_data.get('id', 'unknown')}.png"
    os.makedirs(image_dir, exist_ok=True)
    image_path = os.path.join(image_dir, image_name)
    image.save(image_path)

    # Return the URL for the saved image
    return f"{LOCAL_IMAGE_PATH}/{image_name}"


def _generate_filament_entity_picture(filament_data, image_dir):
    """Generate a filament entity picture with the specified color(s) and save it to the www directory."""

    # Retrieve color(s)
    multi_color_hexes = filament_data.get("multi_color_hexes", "").split(",")
    color_hex = filament_data.get("color_hex", DEFAULT_SPOOL_COLOR_HEX)
    multi_color_direction = filament_data.get("multi_color_direction", "coaxial")

    # Determine colors: prioritize multi_color_hexes if available
    if multi_color_hexes and any(c.strip() for c in multi_color_hexes):
        colors = [c.strip() for c in multi_color_hexes if len(c.strip()) == 6]
    elif color_hex:
        colors = [color_hex]
    else:
        _LOGGER.warning(
            "SpoolManCoordinator: Filament with ID '%s' has no valid color information.",
            filament_data.get("id", "unknown"),
        )
        return None

    # Create image
    image_size = (100, 100)
    image = Image.new("RGB", image_size, int(DEFAULT_SPOOL_COLOR_HEX, 16))
    draw = ImageDraw.Draw(image)

    # Draw colors
    if len(colors) > 1:
        if multi_color_direction == "coaxial":
            step = image_size[0] // len(colors)
            for i, color in enumerate(colors):
                draw.rectangle([
                    (i * step, 0),
                    ((i + 1) * step - 1, image_size[1])
                ], fill=f"#{color}")
        elif multi_color_direction == "longitudinal":
            step = image_size[1] // len(colors)
            for i, color in enumerate(colors):
                draw.rectangle([
                    (0, i * step),
                    (image_size[0], (i + 1) * step - 1)
                ], fill=f"#{color}")
    else:
        # Single color fallback
        draw.rectangle([(0, 0), image_size], fill=f"#{colors[0]}")

    # Save the image
    image_name = f"filament_{filament_data.get('id', 'unknown')}.png"
    os.makedirs(image_dir, exist_ok=True)
    image_path = os.path.join(image_dir, image_name)
    image.save(image_path)

    # Return the URL for the saved image
    return f"{LOCAL_IMAGE_PATH}/{image_name}"
