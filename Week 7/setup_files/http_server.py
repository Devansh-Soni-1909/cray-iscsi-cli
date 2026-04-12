#!/usr/bin/env python3
"""
HTTP Server to read iSCSI target metrics from /host-sys/kernel/config/target/
Exposes metrics via REST API endpoints
"""

import os
import json
import logging
from pathlib import Path
from flask import Flask, jsonify, request

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Target configuration path
TARGET_CONFIG_PATH = os.environ.get(
    "TARGET_CONFIG_PATH", "/host-sys/kernel/config/target"
)


def read_file_content(file_path):
    """
    Read content from a file, handling various file types
    Returns the content or None if file cannot be read
    """
    try:
        if os.path.isfile(file_path):
            with open(file_path, "r") as f:
                content = f.read().strip()
                # Try to convert to number if possible
                try:
                    if "." in content:
                        return float(content)
                    else:
                        return int(content)
                except ValueError:
                    return content
    except (PermissionError, OSError) as e:
        logger.debug(f"Could not read {file_path}: {e}")
        return None
    return None


def scan_directory_recursively(root_path, max_depth=10):
    """
    Recursively scan directory and collect all files and their contents
    Returns a dictionary representation of the directory structure
    """
    if not os.path.isdir(root_path):
        return {}

    result = {}

    try:
        for entry in os.listdir(root_path):
            entry_path = os.path.join(root_path, entry)

            if os.path.isfile(entry_path):
                # Read file content
                content = read_file_content(entry_path)
                result[entry] = content
            elif os.path.isdir(entry_path) and max_depth > 0:
                # Recursively scan subdirectory
                sub_result = scan_directory_recursively(entry_path, max_depth - 1)
                if sub_result or os.path.isdir(entry_path):  # Include even if empty
                    result[entry] = sub_result
            elif os.path.islink(entry_path):
                # Handle symlinks
                try:
                    target = os.readlink(entry_path)
                    result[entry] = f"symlink -> {target}"
                except Exception as e:
                    logger.debug(f"Could not read symlink {entry_path}: {e}")

    except PermissionError as e:
        logger.warning(f"Permission denied reading {root_path}: {e}")
    except Exception as e:
        logger.error(f"Error scanning {root_path}: {e}")

    return result


def flatten_metrics(data, prefix=""):
    """
    Flatten nested dictionary into key-value pairs for easier metrics consumption
    """
    metrics = {}

    for key, value in data.items():
        full_key = f"{prefix}/{key}" if prefix else key

        if isinstance(value, dict):
            # Recursively flatten nested dictionaries
            nested_metrics = flatten_metrics(value, full_key)
            metrics.update(nested_metrics)
        else:
            metrics[full_key] = value

    return metrics


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return (
        jsonify(
            {
                "status": "healthy",
                "service": "iscsi-target-metrics",
                "config_path": TARGET_CONFIG_PATH,
                "config_exists": os.path.isdir(TARGET_CONFIG_PATH),
            }
        ),
        200,
    )


@app.route("/metrics/raw", methods=["GET"])
def get_metrics_raw():
    """
    Get all metrics in nested JSON format
    Maintains the directory structure of /sys/kernel/config/target/
    """
    if not os.path.isdir(TARGET_CONFIG_PATH):
        return (
            jsonify(
                {
                    "error": f"Configuration path {TARGET_CONFIG_PATH} not found",
                    "status": "error",
                }
            ),
            404,
        )

    try:
        metrics = scan_directory_recursively(TARGET_CONFIG_PATH)
        return (
            jsonify(
                {
                    "status": "success",
                    "config_path": TARGET_CONFIG_PATH,
                    "metrics": metrics,
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error reading metrics: {e}")
        return jsonify({"error": str(e), "status": "error"}), 500


@app.route("/metrics/flat", methods=["GET"])
def get_metrics_flat():
    """
    Get all metrics in flattened format (path/key notation)
    Easier for consumption by monitoring systems
    """
    if not os.path.isdir(TARGET_CONFIG_PATH):
        return (
            jsonify(
                {
                    "error": f"Configuration path {TARGET_CONFIG_PATH} not found",
                    "status": "error",
                }
            ),
            404,
        )

    try:
        nested_metrics = scan_directory_recursively(TARGET_CONFIG_PATH)
        flat_metrics = flatten_metrics(nested_metrics)
        return (
            jsonify(
                {
                    "status": "success",
                    "config_path": TARGET_CONFIG_PATH,
                    "metric_count": len(flat_metrics),
                    "metrics": flat_metrics,
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error reading metrics: {e}")
        return jsonify({"error": str(e), "status": "error"}), 500


@app.route("/metrics/section/<section>", methods=["GET"])
def get_metrics_section(section):
    """
    Get metrics for a specific section (e.g., /metrics/section/iscsi)
    """
    if not os.path.isdir(TARGET_CONFIG_PATH):
        return (
            jsonify(
                {
                    "error": f"Configuration path {TARGET_CONFIG_PATH} not found",
                    "status": "error",
                }
            ),
            404,
        )

    section_path = os.path.join(TARGET_CONFIG_PATH, section)

    if not os.path.isdir(section_path):
        return (
            jsonify(
                {
                    "error": f"Section {section} not found at {section_path}",
                    "status": "error",
                    "available_sections": (
                        list(os.listdir(TARGET_CONFIG_PATH))
                        if os.path.isdir(TARGET_CONFIG_PATH)
                        else []
                    ),
                }
            ),
            404,
        )

    try:
        metrics = scan_directory_recursively(section_path)
        return (
            jsonify(
                {
                    "status": "success",
                    "section": section,
                    "path": section_path,
                    "metrics": metrics,
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error reading {section} metrics: {e}")
        return jsonify({"error": str(e), "status": "error"}), 500


@app.route("/config/available-sections", methods=["GET"])
def available_sections():
    """
    List all available sections/directories in the target config
    """
    if not os.path.isdir(TARGET_CONFIG_PATH):
        return (
            jsonify(
                {
                    "error": f"Configuration path {TARGET_CONFIG_PATH} not found",
                    "status": "error",
                }
            ),
            404,
        )

    try:
        sections = []
        for entry in os.listdir(TARGET_CONFIG_PATH):
            entry_path = os.path.join(TARGET_CONFIG_PATH, entry)
            if os.path.isdir(entry_path):
                sections.append(entry)

        return (
            jsonify(
                {
                    "status": "success",
                    "config_path": TARGET_CONFIG_PATH,
                    "available_sections": sorted(sections),
                    "count": len(sections),
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error listing sections: {e}")
        return jsonify({"error": str(e), "status": "error"}), 500


@app.route("/info", methods=["GET"])
def info():
    """Get service information"""
    return (
        jsonify(
            {
                "service": "iSCSI Target Metrics HTTP Server",
                "version": "1.0.0",
                "endpoints": {
                    "GET /health": "Health check",
                    "GET /info": "Service information",
                    "GET /config/available-sections": "List available sections",
                    "GET /metrics/raw": "Get all metrics (nested JSON)",
                    "GET /metrics/flat": "Get all metrics (flattened)",
                    "GET /metrics/section/<section>": "Get metrics for specific section",
                },
                "config_path": TARGET_CONFIG_PATH,
                "config_available": os.path.isdir(TARGET_CONFIG_PATH),
            }
        ),
        200,
    )


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return (
        jsonify(
            {
                "error": "Endpoint not found",
                "status": "error",
                "message": "Try GET /info for available endpoints",
            }
        ),
        404,
    )


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error", "status": "error"}), 500


if __name__ == "__main__":
    logger.info(f"Starting iSCSI Target Metrics HTTP Server")
    logger.info(f"Config path: {TARGET_CONFIG_PATH}")
    logger.info(f"Config path exists: {os.path.isdir(TARGET_CONFIG_PATH)}")

    # Run Flask app
    app.run(host="0.0.0.0", port=9000, debug=False)
