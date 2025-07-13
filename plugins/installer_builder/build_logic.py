import os
import sys
import shutil
import tempfile
import struct
import subprocess
from pathlib import Path
from typing import Callable, Dict, Any

class BuildLogic:
    """Generates a dynamic NSIS script from a config dictionary and runs the build."""

    # Color mapping for HTML log output
    COLOR_MAP = {
        "HEADER": "#E5C07B",
        "OKBLUE": "#61AFEF",
        "OKGREEN": "#98C379",
        "FAIL": "#E06C75",
        "WARN": "#D19A66",
        "DEFAULT": "#ABB2BF"
    }

    def __init__(self, log_callback: Callable[[str, str], None]):
        """
        Initializes the build logic engine.

        Args:
            log_callback: A function to send real-time log messages to the UI.
                          It should accept (message, color_hex_string).
        """
        self.log = log_callback
        # Create a unique temporary directory for this build session
        self.temp_dir = Path(tempfile.gettempdir()) / f"puffin_builder_{os.getpid()}"
        self.generated_nsi_path = self.temp_dir / "generated_script.nsi"
        self._cleanup()

    def _cleanup(self):
        """Ensures the temporary build asset directory is clean before a run."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.temp_dir.mkdir(exist_ok=True, parents=True)

    def log_step(self, message: str):
        """Logs a major step header to the UI."""
        self.log(f"\n===== {message} =====", self.COLOR_MAP["HEADER"])

    def run_full_build(self, config: Dict[str, Any]) -> tuple[bool, str]:
        """
        Executes the entire installer build process based on the configuration.

        Args:
            config: The master dictionary containing all metadata and paths.

        Returns:
            A tuple (success_boolean, final_message_string).
        """
        try:
            self.log_step("Validating Configuration")
            self._validate_config(config)

            self.log_step("Preparing Installer Assets")
            self._generate_installer_assets(config)
            
            self.log_step("Generating Custom NSIS Script")
            nsi_script_content = self._generate_nsi_script(config)
            self.generated_nsi_path.write_text(nsi_script_content, encoding='utf-8')
            self.log("Dynamically generated NSIS script.", self.COLOR_MAP["DEFAULT"])

            self.log_step("Compiling Installer with NSIS")
            nsis_path = config['build']['nsis_path']
            cmd = [nsis_path, str(self.generated_nsi_path)]
            self._run_command(cmd)

            output_file = Path(config['build']['output_dir']) / f"{config['metadata']['app_name']}_{config['metadata']['version']}_Setup.exe"
            final_message = f"Build Complete! Installer saved to:\n{output_file}"
            self.log(final_message, self.COLOR_MAP["OKGREEN"])
            return True, final_message

        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
            self.log(error_message, self.COLOR_MAP["FAIL"])
            return False, error_message
        finally:
            self._cleanup()

    def _validate_config(self, config: Dict):
        """Raises exceptions if the configuration is missing required parts."""
        if not Path(config['build']['source_dir']).is_dir():
            raise FileNotFoundError("Application Source Directory not found.")
            
        main_exe_path = Path(config['build']['source_dir']) / config['metadata']['main_exe']
        if not main_exe_path.is_file():
            raise FileNotFoundError(f"Main Executable '{config['metadata']['main_exe']}' was not found in the source directory.")
        
        if not Path(config['build']['nsis_path']).is_file():
            raise FileNotFoundError("The path to makensis.exe is not valid.")
            
        self.log("Configuration validated successfully.", self.COLOR_MAP["OKGREEN"])

    def _generate_nsi_script(self, config: Dict[str, Any]) -> str:
        """Constructs the final NSI script content by populating the template."""
        template_path = Path(__file__).parent / "assets" / "template.nsi"
        content = template_path.read_text(encoding='utf-8')
        
        b_conf, m_conf, c_conf, s_conf = (config['build'], config['metadata'], config.get('components', []), config.get('shortcuts', []))
        
        # --- Generate Defines ---
        defines = [f'!define {k.upper()} "{v}"' for k, v in m_conf.items()]
        installer_path = Path(b_conf["output_dir"]) / f"{m_conf['app_name']}_{m_conf['version']}_Setup.exe"
        defines.extend([
            f'!define OUT_FILE "{installer_path.resolve()}"',
            f'!define ASSETS_DIR "{self.temp_dir.resolve()}"'
        ])
        if lic_path := b_conf.get('license_path'): defines.append(f'!define LICENSE_FILE "{Path(lic_path).resolve()}"')
        
        # Determine the correct installer icon to use
        icon_path = b_conf.get('installer_icon_path') or self.temp_dir / 'installer_icon.ico'
        defines.append(f'!define INSTALLER_ICON "{Path(icon_path).resolve()}"')

        # Create Section ID defines for reference
        section_ids = {comp['id']: f"SEC{i+1}" for i, comp in enumerate(c_conf)}
        for comp_id, sec_var in section_ids.items(): defines.append(f"!define {comp_id.upper()} {sec_var}")

        # --- Generate Descriptions for Components Page ---
        descriptions = [f'  !insertmacro MUI_DESCRIPTION_TEXT ${{{section_ids[comp["id"]]}}} "{comp["description"]}"' for comp in c_conf]

        # --- Generate Install and Uninstall Sections ---
        install_sections, uninstall_sections = self._generate_sections(config, section_ids)
        
        # --- Replace Placeholders in Template ---
        content = content.replace(';!DEFINE_BLOCK!', "\n".join(defines))
        content = content.replace(';!COMPONENT_DESCRIPTIONS!', "\n".join(descriptions))
        content = content.replace(';!INSTALL_SECTIONS!', install_sections)
        content = content.replace(';!UNINSTALL_SECTIONS!', uninstall_sections)
        
        return content

    def _generate_sections(self, config, section_ids) -> tuple[str, str]:
        """Generates all the Section blocks for installation and uninstallation."""
        inst_list, uninst_list = [], []
        source_dir = Path(config['build']['source_dir'])
        shortcut_icon = config['build'].get('app_shortcut_icon_path')
        
        # Add a placeholder for uninstall logic to avoid crashing if no components exist
        if not config.get('components'): return "", 'Section "Uninstall"\n  RMDir /r "$INSTDIR"\nSectionEnd'

        for i, comp in enumerate(config.get('components', [])):
            sec_var = section_ids[comp['id']]
            flags = "/o" if comp.get('required') else ""
            
            inst_commands = [f'  SetOutPath "$INSTDIR\\{os.path.dirname(comp["source_path"])}"', f'  File /r "{source_dir / comp["source_path"]}"']
            uninst_commands = [f'  RMDir /r "$INSTDIR\\{comp["source_path"]}"']
            
            if i == 0: # This is the main/required component
                inst_commands.append('  WriteUninstaller "$INSTDIR\\uninstall.exe"')
                # If a custom icon for shortcuts is specified, copy it into the install dir
                if shortcut_icon:
                    inst_commands.append(f'  SetOutPath "$INSTDIR"'); inst_commands.append(f'  File /oname=app_icon.ico "{Path(shortcut_icon).resolve()}"')
                
                # Add all shortcuts to the main component's installation section
                for sc in config.get('shortcuts', []):
                    target = f'"$INSTDIR\\{sc["target"]}"'
                    link_path = f'"{sc["location"]}\\{sc["name"]}.lnk"'
                    icon_to_use = '"$INSTDIR\\app_icon.ico"' if shortcut_icon and sc['target'] == config['metadata']['main_exe'] else target
                    
                    inst_commands.append(f'  CreateDirectory "{sc["location"]}"')
                    inst_commands.append(f'  CreateShortCut {link_path} {target} "" {icon_to_use}')
                    uninst_commands.append(f'  Delete {link_path}')
            
            inst_list.append(f'Section "{comp["name"]}" {sec_var}\n{"\n".join(inst_commands)}\nSectionEnd')
            uninst_list.append(f'Section un.{comp["name"]}\n{"\n".join(uninst_commands)}\nSectionEnd')
            
        # The main Uninstall section to clean up common resources
        main_uninst_section = (f'Section "Uninstall"\n  '
                               f'RMDir /r "$SMPROGRAMS\\{config["metadata"]["app_name"]}"\n  '
                               f'DeleteRegKey HKLM "${{PRODUCT_UNINST_KEY}}"\n'
                               'SectionEnd')

        return "\n".join(inst_list), "\n".join(uninst_list) + "\n" + main_uninst_section
        
    def _run_command(self, command: list):
        """Executes a command-line process and logs its output in real-time."""
        cmd_str = ' '.join(f'"{c}"' if ' ' in str(c) else str(c) for c in command)
        self.log(f"Executing: {cmd_str}", self.COLOR_MAP["OKBLUE"])

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='ignore')
        
        for line in iter(process.stdout.readline, ''):
            if line: self.log(line.strip(), self.COLOR_MAP["DEFAULT"])
        
        process.wait()

        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd_str, "NSIS compilation failed. Check the log for details.")

    # --- Asset Generation (identical to previous version) ---
    def _create_ico(self, size, color, path):
        color_hex = color.lstrip('#')
        bgra = tuple(int(color_hex[i:i+2], 16) for i in (4,2,0)) + (255,)
        dib = struct.pack('<lllHHLLllLL', 40, size, size*2, 1, 32, 0, 0, 0, 0, 0, 0)
        dib += bytearray(struct.pack('<BBBB',*bgra)*(size*size))
        dib += bytearray([0x00]*(size*size//8))
        with open(path, 'wb') as f: f.write(struct.pack('<HHH',0,1,1)+struct.pack('<BBBBHHLL',size,size,0,0,1,32,len(dib),22)+dib)
        self.log(f"Generated asset: {path.name}", self.COLOR_MAP["OKGREEN"])

    def _create_bmp(self, w, h, color, path):
        color_hex = color.lstrip('#')
        bgr = tuple(int(color_hex[i:i + 2], 16) for i in (4, 2, 0))
        pad = (4 - (w * 3) % 4) % 4
        with open(path, 'wb') as f:
            f.write(b'BM' + struct.pack('<LHHLLLLllHHLLLLLL', 122, 0, 0, 54, 40, w, h, 1, 24, 0, w*h*3+pad*h, 0,0,0,0))
            for _ in range(h): f.write((struct.pack('BBB', *bgr) * w) + (b'\x00' * pad))
        self.log(f"Generated asset: {path.name}", self.COLOR_MAP["OKGREEN"])