set(IDF_TARGET esp32c6)

set(SDKCONFIG_DEFAULTS
    boards/sdkconfig.base
    boards/sdkconfig.riscv
    boards/sdkconfig.c6
    boards/sdkconfig.ble
)

set(MICROPY_FROZEN_MANIFEST ${MICROPY_BOARD_DIR}/manifest.py)
