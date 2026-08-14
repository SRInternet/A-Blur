; A-Blur NSIS installer script
!include "MUI2.nsh"

!ifndef BUILD_SRC
  !define BUILD_SRC "dist/A-Blur"
!endif
!ifndef OUT_DIR
  !define OUT_DIR "."
!endif

!define PRODUCT_NAME "A-Blur"
!define PRODUCT_VERSION "0.3"
!define MUI_ICON "blur_ico.ico"
!define MUI_UNICON "blur_ico.ico"

Name "${PRODUCT_NAME}"
OutFile "${OUT_DIR}/A-Blur-Setup.exe"
InstallDir "$LOCALAPPDATA/Programs/A-Blur"
RequestExecutionLevel user

!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

; Finish page: "Run A-Blur" checkbox + "Create desktop shortcut" checkbox
!define MUI_FINISHPAGE_RUN "$INSTDIR/A-Blur.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Run ${PRODUCT_NAME}"
!define MUI_FINISHPAGE_SHOWREADME ""
!define MUI_FINISHPAGE_SHOWREADME_CHECKED
!define MUI_FINISHPAGE_SHOWREADME_TEXT "Create a desktop shortcut"
!define MUI_FINISHPAGE_SHOWREADME_FUNCTION CreateDesktopShortcut
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Function CreateDesktopShortcut
  CreateShortcut "$DESKTOP/${PRODUCT_NAME}.lnk" "$INSTDIR/A-Blur.exe"
FunctionEnd

Section "Main" SEC01
  SetOutPath "$INSTDIR"
  File /r "${BUILD_SRC}\*"
  WriteUninstaller "$INSTDIR/Uninstall.exe"

  CreateDirectory "$SMPROGRAMS/${PRODUCT_NAME}"
  CreateShortcut "$SMPROGRAMS/${PRODUCT_NAME}/${PRODUCT_NAME}.lnk" "$INSTDIR/A-Blur.exe"

  WriteRegStr HKCU "Software/Microsoft/Windows/CurrentVersion/Uninstall/${PRODUCT_NAME}" "DisplayName" "${PRODUCT_NAME}"
  WriteRegStr HKCU "Software/Microsoft/Windows/CurrentVersion/Uninstall/${PRODUCT_NAME}" "UninstallString" "$INSTDIR/Uninstall.exe"
  WriteRegStr HKCU "Software/Microsoft/Windows/CurrentVersion/Uninstall/${PRODUCT_NAME}" "DisplayIcon" "$INSTDIR/A-Blur.exe"
  WriteRegStr HKCU "Software/Microsoft/Windows/CurrentVersion/Uninstall/${PRODUCT_NAME}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKCU "Software/Microsoft/Windows/CurrentVersion/Uninstall/${PRODUCT_NAME}" "DisplayVersion" "${PRODUCT_VERSION}"
SectionEnd

Section "Uninstall"
  Delete "$SMPROGRAMS/${PRODUCT_NAME}/${PRODUCT_NAME}.lnk"
  Delete "$DESKTOP/${PRODUCT_NAME}.lnk"
  RMDir "$SMPROGRAMS/${PRODUCT_NAME}"
  RMDir /r "$INSTDIR"
  DeleteRegKey HKCU "Software/Microsoft/Windows/CurrentVersion/Uninstall/${PRODUCT_NAME}"
SectionEnd
