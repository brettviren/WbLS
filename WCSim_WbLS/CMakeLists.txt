#----------------------------------------------------------------------------
# Setup the project
cmake_minimum_required(VERSION 2.6 FATAL_ERROR)
project(WCSim_WbLS)

#----------------------------------------------------------------------------
# Find Geant4 package, activating all available UI and Vis drivers by default
# You can set WITH_GEANT4_UIVIS to OFF via the command line or ccmake/cmake-gui
# to build a batch mode only executable
#
option(WITH_GEANT4_UIVIS "Build example with Geant4 UI and Vis drivers" ON)
if(WITH_GEANT4_UIVIS)
  find_package(Geant4 REQUIRED ui_all vis_all)
else()
  find_package(Geant4 REQUIRED)
endif()

#----------------------------------------------------------------------------
# Setup Geant4 include directories and compile definitions
# Setup include directory for this project
#
include(${Geant4_USE_FILE})

#----------------------------------------------------------------------------
# Find ROOT (required package)
#
find_package(ROOT QUIET)
if(NOT ROOT_FOUND)
  message(STATUS "G4 Examples: ROOT package not found. --> AnaEx02 example disabled")  
  return()
endif()

#----------------------------------------------------------------------------
# Locate sources and headers for this project
#
include_directories(${PROJECT_SOURCE_DIR}/include 
                    ${PROJECT_SOURCE_DIR}/../shared/include 
                    ${Geant4_INCLUDE_DIR}
                    ${ROOT_INCLUDE_DIR})



#----------------------------------------------------------------------------
# Locate sources and headers for this project
# NB: headers are included so they will show up in IDEs
#
file(GLOB sources ${PROJECT_SOURCE_DIR}/src/*.cc)
file(GLOB headers ${PROJECT_SOURCE_DIR}/include/*.hh)

#----------------------------------------------------------------------------
# Add the executable, and link it to the Geant4 libraries
#
add_executable(wcsim-wbls WCSim_WbLS.cc ${sources} ${headers})
target_link_libraries(wcsim-wbls ${Geant4_LIBRARIES} ${ROOT_LIBRARIES})

#----------------------------------------------------------------------------
# The library for the root dictionary for the output file.
# Note: this currently relies on the dictionary to be manually created
# and committed.
add_library(WCSimRoot SHARED src/WCSimRootEvent.cc src/WCSimRootGeom.cc src/WCSimPmtInfo.cc src/WCSimRootDict.cc)


#----------------------------------------------------------------------------
# Copy all scripts to the build directory, i.e. the directory in which we
# build B1. This is so that we can run the executable directly because it
# relies on these scripts being in the current working directory.
#
set(WCSIM_SCRIPTS
  jobOptions2.mac
  jobOptions.mac
  example_mac_scripts/novis.mac
  tuning_parameters.mac
  vis.mac
  )

foreach(_script ${WCSIM_SCRIPTS})
  configure_file(
    ${PROJECT_SOURCE_DIR}/${_script}
    ${PROJECT_BINARY_DIR}/${_script}
    COPYONLY
    )
endforeach()

#----------------------------------------------------------------------------
# For internal Geant4 use - but has no effect if you build this
# example standalone
#
#add_custom_target(WCSim DEPENDS WCSim)

#----------------------------------------------------------------------------
# Install the executable to 'bin' directory under CMAKE_INSTALL_PREFIX
#
install(TARGETS wcsim-wbls RUNTIME DESTINATION bin)
install(TARGETS WCSimRoot LIBRARY DESTINATION lib)


FILE(GLOB macfiles "${CMAKE_CURRENT_SOURCE_DIR}/*.mac" "${CMAKE_CURRENT_SOURCE_DIR}/example_mac_scripts/*.mac")
install(FILES ${macfiles} DESTINATION examples/mac)

FILE(GLOB cintfiles "${CMAKE_CURRENT_SOURCE_DIR}/example_root_scripts/*.C")
install(FILES ${cintfiles} DESTINATION examples/cint)



