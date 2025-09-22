#!/usr/bin/env python3
"""
Travailleur : Archiveur ZIP
Brique d'archivage qui compresse des fichiers dans une archive ZIP.
"""

import argparse
import json
import os
import sys
import zipfile
import glob
from pathlib import Path
from datetime import datetime


class ArchiveurZip:
    def __init__(self):
        """Initialise l'archiveur avec les arguments de ligne de commande."""
        parser = argparse.ArgumentParser(description='Crée une archive ZIP des fichiers spécifiés')
        parser.add_argument('--nom-archive', required=True,
                          help='Nom de l\'archive ZIP à créer (avec extension .zip)')
        parser.add_argument('--fichiers-a-zipper', required=True,
                          help='JSON array des chemins des fichiers/dossiers à archiver')
        parser.add_argument('--compression', choices=['none', 'deflate', 'bzip2', 'lzma'], 
                          default='deflate',
                          help='Méthode de compression à utiliser')
        parser.add_argument('--inclure-dossiers-vides', action='store_true',
                          help='Inclure les dossiers vides dans l\'archive')
        
        self.args = parser.parse_args()
        
        # Validation et parsing des fichiers à zipper
        try:
            self.fichiers = json.loads(self.args.fichiers_a_zipper)
            if not isinstance(self.fichiers, list):
                raise ValueError("Les fichiers doivent être une liste JSON")
        except json.JSONDecodeError as e:
            print(f"❌ ERREUR: Format JSON invalide - {e}", file=sys.stderr)
            sys.exit(1)
        
        # S'assurer que le nom d'archive a l'extension .zip
        if not self.args.nom_archive.endswith('.zip'):
            self.args.nom_archive += '.zip'
        
        # Mapping des méthodes de compression
        self.compression_methods = {
            'none': zipfile.ZIP_STORED,
            'deflate': zipfile.ZIP_DEFLATED,
            'bzip2': zipfile.ZIP_BZIP2,
            'lzma': zipfile.ZIP_LZMA
        }
    
    def run(self):
        """
        Logique principale : crée une archive ZIP contenant tous les fichiers
        et dossiers spécifiés avec les options de compression demandées.
        """
        try:
            print(f"📦 Création archive ZIP : {self.args.nom_archive}")
            print(f"🗜️  Compression : {self.args.compression}")
            print(f"📁 {len(self.fichiers)} éléments à archiver")
            
            # Validation des fichiers d'entrée
            fichiers_existants = self._validate_input_files()
            
            if not fichiers_existants:
                print("⚠️  Aucun fichier existant trouvé")
                self._create_empty_archive()
                return
            
            # Création de l'archive ZIP
            total_files, total_size = self._create_zip_archive(fichiers_existants)
            
            # Validation de l'archive créée
            if os.path.exists(self.args.nom_archive):
                archive_size = os.path.getsize(self.args.nom_archive)
                compression_ratio = (1 - archive_size / total_size) * 100 if total_size > 0 else 0
                
                print(f"✅ Archive créée avec succès")
                print(f"📊 Statistiques :")
                print(f"   • Fichiers archivés : {total_files}")
                print(f"   • Taille originale : {self._format_size(total_size)}")
                print(f"   • Taille archive : {self._format_size(archive_size)}")
                print(f"   • Ratio compression : {compression_ratio:.1f}%")
                
                # Test d'intégrité de l'archive
                self._test_archive_integrity()
            else:
                print("❌ ERREUR: Archive non créée")
                sys.exit(1)
            
        except Exception as e:
            print(f"❌ ERREUR lors de l'archivage : {e}", file=sys.stderr)
            sys.exit(1)
    
    def _validate_input_files(self):
        """
        Valide et expand les fichiers d'entrée, supportant les wildcards.
        """
        fichiers_existants = []
        
        for item in self.fichiers:
            if '*' in item or '?' in item:
                # Support des wildcards avec glob
                matches = glob.glob(item, recursive=True)
                if matches:
                    fichiers_existants.extend(matches)
                    print(f"🔍 Wildcard '{item}' -> {len(matches)} fichier(s)")
                else:
                    print(f"⚠️  Wildcard '{item}' -> aucune correspondance")
            else:
                # Fichier/dossier spécifique
                if os.path.exists(item):
                    fichiers_existants.append(item)
                    print(f"✅ {item}")
                else:
                    print(f"⚠️  Non trouvé : {item}")
        
        # Suppression des doublons et tri
        fichiers_existants = sorted(list(set(fichiers_existants)))
        
        return fichiers_existants
    
    def _create_zip_archive(self, fichiers_existants):
        """
        Crée l'archive ZIP avec les fichiers validés.
        """
        compression = self.compression_methods[self.args.compression]
        total_files = 0
        total_size = 0
        
        # Préparation du répertoire de sortie
        Path(self.args.nom_archive).parent.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(self.args.nom_archive, 'w', compression=compression, compresslevel=6) as zipf:
            for item in fichiers_existants:
                if os.path.isfile(item):
                    # Fichier individuel
                    file_size = os.path.getsize(item)
                    arcname = os.path.relpath(item)  # Chemin relatif dans l'archive
                    zipf.write(item, arcname=arcname)
                    total_files += 1
                    total_size += file_size
                    print(f"   📄 {arcname} ({self._format_size(file_size)})")
                    
                elif os.path.isdir(item):
                    # Dossier récursif
                    files_added, size_added = self._add_directory_to_zip(zipf, item)
                    total_files += files_added
                    total_size += size_added
                    print(f"   📁 {item}/ ({files_added} fichiers, {self._format_size(size_added)})")
                    
                    # Ajouter le dossier vide si demandé et qu'il est vide
                    if self.args.inclure_dossiers_vides and files_added == 0:
                        zipf.writestr(f"{item}/", "")
                        print(f"   📂 {item}/ (dossier vide)")
        
        return total_files, total_size
    
    def _add_directory_to_zip(self, zipf, directory):
        """
        Ajoute récursivement un dossier à l'archive ZIP.
        """
        files_added = 0
        size_added = 0
        
        for root, dirs, files in os.walk(directory):
            # Ajout des fichiers
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path)
                
                try:
                    file_size = os.path.getsize(file_path)
                    zipf.write(file_path, arcname=arcname)
                    files_added += 1
                    size_added += file_size
                except (OSError, IOError) as e:
                    print(f"⚠️  Erreur fichier {file_path}: {e}")
            
            # Ajout des dossiers vides si demandé
            if self.args.inclure_dossiers_vides:
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    if not os.listdir(dir_path):  # Dossier vide
                        arcname = os.path.relpath(dir_path) + "/"
                        zipf.writestr(arcname, "")
        
        return files_added, size_added
    
    def _create_empty_archive(self):
        """
        Crée une archive ZIP vide avec un fichier README.
        """
        Path(self.args.nom_archive).parent.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(self.args.nom_archive, 'w', zipfile.ZIP_DEFLATED) as zipf:
            readme_content = f"""# Archive Vide
            
Cette archive a été créée le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.

Aucun fichier correspondant aux critères n'a été trouvé :
{chr(10).join(f'- {f}' for f in self.fichiers)}
"""
            zipf.writestr("README.md", readme_content.strip())
        
        print("📦 Archive vide créée avec README")
    
    def _test_archive_integrity(self):
        """
        Teste l'intégrité de l'archive créée.
        """
        try:
            with zipfile.ZipFile(self.args.nom_archive, 'r') as zipf:
                # Test de l'intégrité
                bad_file = zipf.testzip()
                if bad_file:
                    print(f"⚠️  Fichier corrompu dans l'archive : {bad_file}")
                else:
                    print("✅ Intégrité de l'archive vérifiée")
                
                # Information sur le contenu
                info_list = zipf.infolist()
                print(f"📋 Contenu de l'archive : {len(info_list)} éléments")
                
                if len(info_list) <= 10:  # Afficher le détail si pas trop d'éléments
                    for info in info_list:
                        print(f"   • {info.filename} ({self._format_size(info.file_size)})")
                
        except zipfile.BadZipFile as e:
            print(f"❌ Archive corrompue : {e}")
            sys.exit(1)
        except Exception as e:
            print(f"⚠️  Erreur test intégrité : {e}")
    
    def _format_size(self, size_bytes):
        """
        Formate la taille en bytes de manière lisible.
        """
        if size_bytes == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        i = 0
        while size_bytes >= 1024.0 and i < len(units) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {units[i]}"


if __name__ == "__main__":
    archiveur = ArchiveurZip()
    archiveur.run()
