cmake_minimum_required(VERSION 3.21)

project(stm32f103c8t6-blink C ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

# Replace these values when changing the MCU family.
set(MCU_FLAGS
    -mcpu=cortex-m3
    -mthumb
)

set(STM32_DEFINES
    STM32F103xB
    USE_HAL_DRIVER
)

set(LINKER_SCRIPT
    ${CMAKE_CURRENT_SOURCE_DIR}/STM32F103C8Tx_FLASH.ld
)

set(STARTUP_SOURCE
    ${CMAKE_CURRENT_SOURCE_DIR}/startup_stm32f103xb.s
)

file(GLOB_RECURSE CORE_SOURCES CONFIGURE_DEPENDS
    ${CMAKE_CURRENT_SOURCE_DIR}/Core/Src/*.c
)

file(GLOB_RECURSE USER_SOURCES CONFIGURE_DEPENDS
    ${CMAKE_CURRENT_SOURCE_DIR}/User/Src/*.c
)

file(GLOB_RECURSE HAL_SOURCES CONFIGURE_DEPENDS
    ${CMAKE_CURRENT_SOURCE_DIR}/Drivers/STM32F1xx_HAL_Driver/Src/*.c
)

list(FILTER HAL_SOURCES EXCLUDE REGEX ".*_template\\.c$")

if(NOT EXISTS "${LINKER_SCRIPT}")
    message(FATAL_ERROR "Linker script not found: ${LINKER_SCRIPT}")
endif()

if(NOT EXISTS "${STARTUP_SOURCE}")
    message(FATAL_ERROR "Startup file not found: ${STARTUP_SOURCE}")
endif()

add_executable(${PROJECT_NAME}
    ${CORE_SOURCES}
    ${USER_SOURCES}
    ${HAL_SOURCES}
    ${STARTUP_SOURCE}
)

target_include_directories(${PROJECT_NAME} PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/Core/Inc
    ${CMAKE_CURRENT_SOURCE_DIR}/User/Inc
    ${CMAKE_CURRENT_SOURCE_DIR}/Drivers/STM32F1xx_HAL_Driver/Inc
    ${CMAKE_CURRENT_SOURCE_DIR}/Drivers/STM32F1xx_HAL_Driver/Inc/Legacy
    ${CMAKE_CURRENT_SOURCE_DIR}/Drivers/CMSIS/Device/ST/STM32F1xx/Include
    ${CMAKE_CURRENT_SOURCE_DIR}/Drivers/CMSIS/Include
)

target_compile_definitions(${PROJECT_NAME} PRIVATE
    ${STM32_DEFINES}
)

target_compile_options(${PROJECT_NAME} PRIVATE
    ${MCU_FLAGS}
    -Wall
    -Wextra
    -fdata-sections
    -ffunction-sections
    $<$<CONFIG:Debug>:-Og>
    $<$<CONFIG:Debug>:-g3>
    $<$<CONFIG:Release>:-Os>
)

set_source_files_properties(${STARTUP_SOURCE} PROPERTIES
    COMPILE_OPTIONS "-x;assembler-with-cpp"
)

target_link_options(${PROJECT_NAME} PRIVATE
    ${MCU_FLAGS}
    -T${LINKER_SCRIPT}
    -Wl,-Map=${PROJECT_NAME}.map,--cref
    -Wl,--gc-sections
    -Wl,--print-memory-usage
    --specs=nano.specs
    --specs=nosys.specs
)

set_target_properties(${PROJECT_NAME} PROPERTIES
    SUFFIX ".elf"
)

add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_OBJCOPY}
        -O ihex
        $<TARGET_FILE:${PROJECT_NAME}>
        ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}.hex
    COMMAND ${CMAKE_OBJCOPY}
        -O binary
        $<TARGET_FILE:${PROJECT_NAME}>
        ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}.bin
    COMMAND ${CMAKE_SIZE}
        $<TARGET_FILE:${PROJECT_NAME}>
)
