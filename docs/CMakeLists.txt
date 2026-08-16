cmake_minimum_required( VERSION 3.10 FATAL_ERROR )

project( kicad-symbols NONE )

#================================================
# Locations for install targets.
#================================================
if( APPLE )
    # Like all variables, CMAKE_INSTALL_PREFIX can be over-ridden on the command line.
    set( CMAKE_INSTALL_PREFIX "/Library/Application Support/kicad/" CACHE PATH "" )

    # Everything without leading / is relative to CMAKE_INSTALL_PREFIX.
    set( KICAD_LIBRARY symbols )
    set( KICAD_TEMPLATE template )
else()
    # Everything without leading / is relative to CMAKE_INSTALL_PREFIX.
    set( KICAD_DATA share/kicad
         CACHE PATH "Location of KiCad data files." )
    set( KICAD_LIBRARY ${KICAD_DATA}/symbols )
    set( KICAD_TEMPLATE ${KICAD_DATA}/template )
endif()

mark_as_advanced( KICAD_DATA KICAD_LIBRARY )


#================================================
# "make uninstall" rules
#================================================
configure_file(
    "${PROJECT_SOURCE_DIR}/CMakeModules/cmake_uninstall.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake"
    IMMEDIATE @ONLY )

add_custom_target( uninstall
    "${CMAKE_COMMAND}" -P "${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake" )


#================================================
# Installed files.
#================================================

# Install all of the symbol library (.kicad_sym) and simulation model (.sp)
# files in this folder.
file(GLOB sym_and_sim_lib_files "*.kicad_sym" "*.sp")

install(FILES ${sym_and_sim_lib_files}
        DESTINATION ${KICAD_LIBRARY}
        COMPONENT resources)

# Install the default global symbol library table in the template folder.
install(FILES sym-lib-table
        DESTINATION ${KICAD_TEMPLATE}
        COMPONENT resources)
