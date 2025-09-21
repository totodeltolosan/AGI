#!/bin/bash

# RAPPORT D'ANALYSE SYSTÈME AVANCÉ (v3.6 - God Mode++++ - Partie 6 : L'Ultime Évolution IA)
# Généré le : $(date)
# Utilisateur : $(whoami)
# Hôte : $(hostname)

# ==============================================================================
# INTRODUCTION & AVERTISSEMENT
# ==============================================================================
echo -e "\n=============================================================================="
echo -e "[ INTRODUCTION & AVERTISSEMENT - PARTIE 6 : L'Ultime Évolution IA ]"
echo -e "=============================================================================="
echo "Bienvenue dans la sixième et ultime phase de l'analyse God Mode++++."
echo "Ce script va effectuer une vérification complète de toutes les actions précédentes, corriger les dernières anomalies, et vous guider vers l'intégration d'outils d'intelligence artificielle gratuits et optimisés."
echo "Nous allons transformer votre PC en une plateforme plus intelligente, plus performante et plus sécurisée."
echo "Lisez attentivement chaque option et chaque confirmation. La prudence est de mise."
echo "Sauvegardez toujours vos données importantes avant d'effectuer des modifications majeures."
echo -e "\nDébut de l'analyse, des corrections et de l'intégration IA interactive..."
sleep 2

# ==============================================================================
# FONCTIONS UTILITAIRES POUR L'INTERACTIVITÉ
# ==============================================================================

# Fonction pour demander une confirmation robuste
confirm_action() {
    local prompt="$1"
    while true; do
        read -p "$prompt (o/n) " -n 1 -r
        echo
        case $REPLY in
            [Oo]* ) return 0 ;;
            [Nn]* ) return 1 ;;
            * ) echo "Réponse invalide. Veuillez répondre 'o' pour oui ou 'n' pour non." ;;
        esac
    done
}

# Fonction pour afficher un menu et obtenir un choix
display_menu() {
    local title="$1"
    shift
    local options=("$@")
    local choice

    echo -e "\n--- $title ---"
    for i in "${!options[@]}"; do
        echo "$((i+1)). ${options[$i]}"
    done
    echo "0. Retour au menu principal / Quitter"

    while true; do
        read -p "Votre choix : " choice
        if [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 0 && choice <= ${#options[@]} )); then
            echo # Nouvelle ligne après l'entrée
            return "$choice"
        else
            echo "Choix invalide. Veuillez entrer un numéro entre 0 et ${#options[@]}."
        fi
    done
}

# Fonction pour exécuter une commande avec feedback
execute_command() {
    local description="$1"
    local command="$2"
    echo -e "\n[ EXÉCUTION ] $description"
    echo "Commande : $command"
    echo "--- Début de la sortie ---"
    eval "$command" 2>&1
    local exit_code=$?
    echo "--- Fin de la sortie (Code de sortie : $exit_code) ---"
    if [ $exit_code -ne 0 ]; then
        echo "AVERTISSEMENT : La commande a échoué avec le code de sortie $exit_code."
    fi
    return $exit_code
}

# ==============================================================================
# [ 1/6 ] VÉRIFICATION COMPLÈTE DES ACTIONS PRÉCÉDENTES
# ==============================================================================
verify_previous_actions() {
    echo -e "\n=============================================================================="
    echo -e "[ 1/6 ] VÉRIFICATION COMPLÈTE DES ACTIONS PRÉCÉDENTES"
    echo -e "=============================================================================="
    echo "Nous allons passer en revue l'état de chaque point critique abordé jusqu'à présent."

    # --- 1.1. Entropie du système ---
    echo -e "\n--- 1.1. Entropie du système ---"
    ENTROPY_AVAIL=$(cat /proc/sys/kernel/random/entropy_avail)
    echo "Entropie disponible : $ENTROPY_AVAIL bits."
    if (( ENTROPY_AVAIL > 1000 )); then
        echo "STATUT : ✅ Entropie adéquate. Excellent !"
    else
        echo "STATUT : ❌ Entropie toujours basse ($ENTROPY_AVAIL bits). C'est un problème critique."
        echo "Actions requises : Re-vérifier haveged, activer rngd, ajuster les seuils du noyau, vérifier le TPM."
        execute_command "Statut détaillé de haveged" "systemctl status haveged.service --no-pager"
        execute_command "Statut détaillé de rngd" "systemctl status rngd.service --no-pager"
        execute_command "Vérification du module 'tpm_rng'" "lsmod | grep tpm_rng"
        echo "Si rngd n'est pas actif, il est fortement recommandé de l'activer : 'sudo systemctl enable rngd --now'."
        echo "Si l'entropie reste basse, un problème matériel ou de configuration du noyau est probable."
    fi

    # --- 1.2. Pare-feu UFW ---
    echo -e "\n--- 1.2. Pare-feu UFW ---"
    UFW_STATUS=$(sudo ufw status verbose | grep "État")
    echo "$UFW_STATUS"
    if echo "$UFW_STATUS" | grep -q "actif"; then
        echo "STATUT : ✅ UFW est actif. Votre pare-feu est opérationnel."
    else
        echo "STATUT : ❌ UFW est inactif. Votre système est exposé."
        if confirm_action "Voulez-vous ACTIVER UFW avec les règles par défaut (refuser tout entrant, autoriser tout sortant) ?"; then
            execute_command "Configuration UFW : refuser entrant" "sudo ufw default deny incoming"
            execute_command "Configuration UFW : autoriser sortant" "sudo ufw default allow outgoing"
            execute_command "Activation de UFW" "sudo ufw enable"
            echo "UFW activé. Re-vérification :"
            execute_command "Statut UFW après activation" "sudo ufw status verbose"
        else
            echo "Activation de UFW ignorée. C'est une vulnérabilité majeure."
        fi
    fi

    # --- 1.3. Statut Ubuntu Pro ---
    echo -e "\n--- 1.3. Statut Ubuntu Pro ---"
    PRO_STATUS=$(pro security-status --format text)
    echo "$PRO_STATUS"
    if echo "$PRO_STATUS" | grep -q "attached to an Ubuntu Pro subscription"; then
        echo "STATUT : ✅ Votre machine est attachée à Ubuntu Pro. Excellent pour la sécurité !"
    else
        echo "STATUT : ❌ Votre machine n'est PAS attachée à Ubuntu Pro."
        echo "Action requise : Obtenez un jeton et exécutez 'sudo pro attach VOTRE_JETON_ICI'."
    fi

    # --- 1.4. Rétroéclairage du clavier ---
    echo -e "\n--- 1.4. Rétroéclairage du clavier ---"
    execute_command "Statut du service de contournement kbd-backlight-fix.service" "systemctl status kbd-backlight-fix.service --no-pager"
    execute_command "Statut du service original systemd-backlight" "systemctl status systemd-backlight@leds:dell::kbd_backlight.service --no-pager"
    if systemctl is-masked systemd-backlight@leds:dell::kbd_backlight.service &> /dev/null; then
        echo "STATUT : ✅ Le service original est masqué. Le contournement devrait être en place."
        if confirm_action "Le rétroéclairage de votre clavier fonctionne-t-il correctement au démarrage ?"; then
            echo "STATUT : ✅ Rétroéclairage fonctionnel. Problème résolu."
        else
            echo "STATUT : ❌ Le rétroéclairage ne fonctionne pas. Investigation supplémentaire nécessaire."
            echo "Vérifiez le contenu de '/etc/systemd/system/kbd-backlight-fix.service' et les logs : 'journalctl -u kbd-backlight-fix.service --no-pager'."
        fi
    else
        echo "STATUT : ❌ Le service original n'est pas masqué. Il pourrait y avoir des conflits."
        if confirm_action "Voulez-vous masquer le service 'systemd-backlight@leds:dell::kbd_backlight.service' maintenant ?"; then
            execute_command "Masquage du service original" "sudo systemctl mask systemd-backlight@leds:dell::kbd_backlight.service"
            echo "Service original masqué."
        fi
    fi

    # --- 1.5. Erreurs ACPI ---
    echo -e "\n--- 1.5. Erreurs ACPI ---"
    ACPI_ERRORS=$(sudo journalctl -k -p err | grep "ACPI Error" | tail -n 10)
    if [ -z "$ACPI_ERRORS" ]; then
        echo "STATUT : ✅ Aucune erreur ACPI critique récente détectée. Excellent !"
    else
        echo "STATUT : ❌ Des erreurs ACPI persistent."
        echo "$ACPI_ERRORS"
        echo "Actions requises : Vérifier les mises à jour du BIOS Dell, modifier les options GRUB ('acpi_osi=Linux acpi_rev_override=1')."
    fi

    # --- 1.6. Services FluidSynth et JACK ---
    echo -e "\n--- 1.6. Services FluidSynth et JACK ---"
    if ! dpkg -l | grep -q fluidsynth && ! dpkg -l | grep -q jackd1 && ! dpkg -l | grep -q jack-mixer; then
        echo "STATUT : ✅ FluidSynth et JACK ne sont pas installés. Problèmes résolus."
    else
        echo "STATUT : ❌ Des paquets FluidSynth/JACK sont toujours présents."
        execute_command "Liste des paquets FluidSynth/JACK" "dpkg -l | grep -E 'fluidsynth|jackd1|jack-mixer'"
        if confirm_action "Voulez-vous purger ces paquets maintenant ?"; then
            execute_command "Purge des paquets FluidSynth/JACK" "sudo apt purge -y fluidsynth jackd1 jack-mixer"
        fi
    fi
    execute_command "Processus liés à JACK/FluidSynth" "ps aux | grep -i \"jack\|fluid\" | grep -v grep"
    if [ $? -eq 0 ]; then
        echo "STATUT : ❌ Des processus liés à JACK/FluidSynth sont toujours actifs. Vous devrez les arrêter manuellement ou identifier l'application qui les lance."
    else
        echo "STATUT : ✅ Aucun processus lié à JACK/FluidSynth détecté."
    fi

    # --- 1.7. Périphérique USB RODE NT-USB+ ---
    echo -e "\n--- 1.7. Périphérique USB RODE NT-USB+ ---"
    echo "STATUT : ✅ Le micro RODE NT-USB+ fonctionne malgré l'erreur 'usb 1-3: device not accepting address 7, error -71'."
    echo "Cette erreur est considérée comme mineure et non bloquante pour la fonctionnalité."

    echo -e "\n--- 1.8. Nettoyage des paquets avec configurations résiduelles ---"
    RESIDUAL_PACKAGES=$(dpkg -l | grep "^rc" | awk '{print $2}')
    if [ -z "$RESIDUAL_PACKAGES" ]; then
        echo "STATUT : ✅ Aucun paquet avec configuration résiduelle détecté. Le système est propre."
    else
        echo "STATUT : ❌ Des paquets avec configurations résiduelles sont toujours détectés."
        echo "$RESIDUAL_PACKAGES"
        if confirm_action "Voulez-vous purger ces paquets maintenant ?"; then
            execute_command "Purge des paquets résiduels" "sudo apt purge -y $RESIDUAL_PACKAGES"
        fi
    fi

    echo -e "\n--- 1.9. Optimisation du temps de démarrage : NetworkManager-wait-online.service ---"
    if systemctl is-enabled NetworkManager-wait-online.service &> /dev/null; then
        echo "STATUT : ❌ NetworkManager-wait-online.service est toujours actif."
        if confirm_action "Voulez-vous désactiver NetworkManager-wait-online.service pour accélérer le démarrage ?"; then
            execute_command "Désactivation de NetworkManager-wait-online.service" "sudo systemctl disable NetworkManager-wait-online.service --now"
        fi
    else
        echo "STATUT : ✅ NetworkManager-wait-online.service est désactivé. Démarrage optimisé."
    fi

    echo -e "\nAppuyez sur Entrée pour continuer vers le menu principal..."
    read -r
}

# ==============================================================================
# [ 2/6 ] INSTALLATION ET CONFIGURATION DES OUTILS MANQUANTS
# ==============================================================================
handle_tool_installation() {
    while true; do
        display_menu "INSTALLATION ET CONFIGURATION DES OUTILS" \
            "1. Installer/Vérifier cpufrequtils" \
            "2. Installer/Vérifier preload" \
            "3. Installer/Vérifier fzf" \
            "4. Installer/Vérifier TLP (gestion énergie)" \
            "5. Installer/Vérifier PowerTOP (gestion énergie)" \
            "6. Installer/Vérifier Logwatch (audit logs)" \
            "7. Installer/Vérifier Fail2ban (sécurité)" \
            "8. Installer/Vérifier zram-tools (swap compressé)" \
            "9. Installer/Vérifier tmpwatch (nettoyage temporaires)" \
            "10. Installer/Vérifier ncdu (analyse espace disque)" \
            "11. Installer/Vérifier e2fsprogs (pour e4defrag)" \
            "12. Installer/Vérifier apt-listbugs (bugs paquets)" \
            "13. Installer/Vérifier qemu-kvm, libvirt, virt-manager (virtualisation)" \
            "14. Installer/Vérifier rng-tools (pour rngd)"
        local choice=$?

        case $choice in
            1) # cpufrequtils
                if ! command -v cpufreq-info &> /dev/null; then
                    if confirm_action "cpufrequtils n'est pas installé. L'installer ?"; then
                        execute_command "Installation de cpufrequtils" "sudo apt install -y cpufrequtils"
                    fi
                else
                    echo "cpufrequtils est déjà installé."
                fi
                execute_command "Affichage des informations CPUFreq" "cpufreq-info"
                ;;
            2) # preload
                if ! command -v preload &> /dev/null; then
                    if confirm_action "preload n'est pas installé. L'installer ?"; then
                        execute_command "Installation de preload" "sudo apt install -y preload"
                    fi
                else
                    echo "preload est déjà installé."
                fi
                execute_command "Statut du service preload" "systemctl status preload.service --no-pager"
                if command -v preload &> /dev/null && ! systemctl is-enabled preload.service &> /dev/null; then
                    if confirm_action "Le service preload n'est pas activé. L'activer ?"; then
                        execute_command "Activation de preload.service" "sudo systemctl enable preload.service --now"
                    fi
                fi
                ;;
            3) # fzf
                if ! command -v fzf &> /dev/null; then
                    if confirm_action "fzf n'est pas installé. L'installer ?"; then
                        execute_command "Installation de fzf" "sudo apt install -y fzf"
                    fi
                else
                    echo "fzf est déjà installé."
                fi
                echo "Pour intégrer fzf à votre shell (bash/zsh), suivez les instructions de post-installation de fzf ou consultez sa documentation."
                ;;
            4) # TLP
                if ! command -v tlp &> /dev/null; then
                    if confirm_action "TLP n'est pas installé. L'installer (alternative à PowerTOP) ?"; then
                        execute_command "Installation de TLP" "sudo apt install -y tlp tlp-rdw"
                    fi
                else
                    echo "TLP est déjà installé."
                fi
                execute_command "Statut du service TLP" "systemctl status tlp.service --no-pager"
                if command -v tlp &> /dev/null && ! systemctl is-enabled tlp.service &> /dev/null; then
                    if confirm_action "Le service TLP n'est pas activé. L'activer ?"; then
                        execute_command "Activation de tlp.service" "sudo systemctl enable tlp.service --now"
                    fi
                fi
                execute_command "Rapport TLP" "sudo tlp-stat -s"
                ;;
            5) # PowerTOP
                if ! command -v powertop &> /dev/null; then
                    if confirm_action "PowerTOP n'est pas installé. L'installer (alternative à TLP) ?"; then
                        execute_command "Installation de PowerTOP" "sudo apt install -y powertop"
                    fi
                else
                    echo "PowerTOP est déjà installé."
                fi
                if command -v powertop &> /dev/null; then
                    echo "Pour utiliser PowerTOP en mode auto-tune, exécutez 'sudo powertop --auto-tune'."
                fi
                ;;
            6) # Logwatch
                if ! command -v logwatch &> /dev/null; then
                    if confirm_action "Logwatch n'est pas installé. L'installer ?"; then
                        execute_command "Installation de Logwatch" "sudo apt install -y logwatch"
                    fi
                else
                    echo "Logwatch est déjà installé."
                fi
                if command -v logwatch &> /dev/null; then
                    echo "Logwatch génère des rapports quotidiens. Configurez-le via '/etc/logwatch/conf/logwatch.conf'."
                    if confirm_action "Voulez-vous générer un rapport Logwatch maintenant (peut être long) ?"; then
                        execute_command "Génération rapport Logwatch" "sudo logwatch --detail High --range today"
                    fi
                fi
                ;;
            7) # Fail2ban
                if ! command -v fail2ban-client &> /dev/null; then
                    if confirm_action "Fail2ban n'est pas installé. L'installer ?"; then
                        execute_command "Installation de Fail2ban" "sudo apt install -y fail2ban"
                    fi
                else
                    echo "Fail2ban est déjà installé."
                fi
                execute_command "Statut du service Fail2ban" "sudo systemctl status fail2ban.service --no-pager"
                if command -v fail2ban-client &> /dev/null && ! systemctl is-enabled fail2ban.service &> /dev/null; then
                    if confirm_action "Le service Fail2ban n'est pas activé. L'activer ?"; then
                        execute_command "Activation de fail2ban.service" "sudo systemctl enable fail2ban.service --now"
                    fi
                fi
                if command -v fail2ban-client &> /dev/null; then
                    echo "Configurez Fail2ban via '/etc/fail2ban/jail.local'."
                fi
                ;;
            8) # zram-tools
                if ! command -v zramctl &> /dev/null; then
                    if confirm_action "zram-tools n'est pas installé. L'installer ?"; then
                        execute_command "Installation de zram-tools" "sudo apt install -y zram-tools"
                    fi
                else
                    echo "zram-tools est déjà installé."
                fi
                execute_command "Statut de zram" "zramctl"
                if command -v zramctl &> /dev/null && ! systemctl is-enabled zramswap.service &> /dev/null; then
                    if confirm_action "Le service zramswap n'est pas activé. L'activer ?"; then
                        execute_command "Activation de zramswap.service" "sudo systemctl enable zramswap.service --now"
                    fi
                fi
                echo "Configurez zram via '/etc/default/zramswap'."
                ;;
            9) # tmpwatch
                if ! command -v tmpwatch &> /dev/null; then
                    if confirm_action "tmpwatch n'est pas installé. L'installer ?"; then
                        execute_command "Installation de tmpwatch" "sudo apt install -y tmpwatch"
                    fi
                else
                    echo "tmpwatch est déjà installé."
                fi
                if command -v tmpwatch &> /dev/null; then
                    echo "tmpwatch peut nettoyer les répertoires temporaires. Exemple : 'sudo tmpwatch 7d /tmp'."
                    if confirm_action "Voulez-vous exécuter 'sudo tmpwatch 7d /tmp' maintenant ?"; then
                        execute_command "Nettoyage de /tmp avec tmpwatch" "sudo tmpwatch 7d /tmp"
                    fi
                fi
                ;;
            10) # ncdu
                if ! command -v ncdu &> /dev/null; then
                    if confirm_action "ncdu n'est pas installé. L'installer ?"; then
                        execute_command "Installation de ncdu" "sudo apt install -y ncdu"
                    fi
                else
                    echo "ncdu est déjà installé."
                fi
                if command -v ncdu &> /dev/null; then
                    echo "Pour une analyse interactive de l'espace disque, exécutez 'ncdu /home/toni'."
                fi
                ;;
            11) # e2fsprogs (e4defrag)
                if ! command -v e4defrag &> /dev/null; then
                    if confirm_action "e2fsprogs (qui contient e4defrag) n'est pas installé. L'installer ?"; then
                        execute_command "Installation de e2fsprogs" "sudo apt install -y e2fsprogs"
                    fi
                else
                    echo "e4defrag est déjà installé."
                fi
                if command -v e4defrag &> /dev/null; then
                    echo "e4defrag peut défragmenter des fichiers/répertoires sur des partitions ext4. Exemple : 'sudo e4defrag /dev/sda2' (avec prudence)."
                fi
                ;;
            12) # apt-listbugs
                if ! dpkg -s apt-listbugs &> /dev/null; then
                    if confirm_action "apt-listbugs n'est pas installé. L'installer ?"; then
                        execute_command "Installation de apt-listbugs" "sudo apt install -y apt-listbugs"
                    fi
                else
                    echo "apt-listbugs est déjà installé."
                fi
                if dpkg -s apt-listbugs &> /dev/null; then
                    echo "apt-listbugs vous alertera des bugs critiques lors des mises à jour."
                fi
                ;;
            13) # KVM/QEMU
                if ! command -v kvm &> /dev/null; then
                    if confirm_action "KVM/QEMU et les outils de virtualisation ne sont pas installés. Les installer ?"; then
                        execute_command "Installation de KVM/QEMU et outils" "sudo apt install -y qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virt-manager"
                        execute_command "Ajout de l'utilisateur au groupe libvirt" "sudo usermod -aG libvirt toni"
                        execute_command "Ajout de l'utilisateur au groupe kvm" "sudo usermod -aG kvm toni"
                        echo "Un redémarrage de la session est nécessaire pour que les changements de groupe prennent effet."
                    fi
                else
                    echo "KVM/QEMU et les outils sont déjà installés."
                fi
                ;;
            14) # rng-tools
                if ! command -v rngd &> /dev/null; then
                    if confirm_action "rng-tools n'est pas installé. L'installer (pour rngd, qui utilise le RNG matériel) ?"; then
                        execute_command "Installation de rng-tools" "sudo apt install -y rng-tools"
                    fi
                else
                    echo "rng-tools est déjà installé."
                fi
                execute_command "Statut du service rngd" "systemctl status rngd.service --no-pager"
                if command -v rngd &> /dev/null && ! systemctl is-enabled rngd.service &> /dev/null; then
                    if confirm_action "Le service rngd n'est pas activé. L'activer ?"; then
                        execute_command "Activation de rngd.service" "sudo systemctl enable rngd.service --now"
                    fi
                fi
                ;;
            0) break ;;
        esac
        echo -e "\nAppuyez sur Entrée pour continuer..."
        read -r
    done
}

# ==============================================================================
# [ 3/6 ] OPTIMISATIONS & AMÉLIORATIONS GÉNÉRALES
# ==============================================================================
handle_general_optimizations() {
    while true; do
        display_menu "OPTIMISATIONS & AMÉLIORATIONS GÉNÉRALES" \
            "1. Nettoyage des anciennes versions de Snaps" \
            "2. Gestion des fichiers volumineux dans le répertoire personnel" \
            "3. Nettoyage des caches système (APT, vignettes)" \
            "4. Optimisation des paramètres du noyau pour les SSD (noatime)"
        local choice=$?

        case $choice in
            1) # Nettoyage Snaps
                echo -e "\n--- 3.1. Nettoyage des anciennes versions de Snaps ---"
                echo "Une purge régulière des anciennes révisions de Snaps peut libérer de l'espace disque."
                if confirm_action "Voulez-vous purger les anciennes révisions de Snaps maintenant ?"; then
                    set -eu
                    snap list --all | awk '/disabled/{print $1, $3}' | while read snapname revision; do
                        echo "Suppression de l'ancienne révision $revision du snap $snapname..."
                        execute_command "Suppression Snap $snapname rev $revision" "sudo snap remove \"$snapname\" --revision=\"$revision\""
                    done
                    echo "Nettoyage des anciennes révisions de Snaps terminé."
                    echo "Vous pouvez également exécuter 'sudo snap refresh --hold=false --cleanup' pour un nettoyage plus général."
                else
                    echo "Nettoyage des anciennes révisions de Snaps ignoré."
                fi
                ;;
            2) # Gestion des fichiers volumineux
                echo -e "\n--- 3.2. Gestion des fichiers volumineux dans le répertoire personnel ---"
                echo "Rappel des dossiers volumineux :"
                echo "9,0G /home/toni/.ollama/models/blobs"
                echo "9,0G /home/toni/.ollama/models"
                echo "6,1G /home/toni/venv"
                echo "4,9G /home/toni/miniconda3"
                echo "4,8G /home/toni/Documents/connaisance a implenter plus tard"
                echo "4,4G /home/toni/Desktop"
                echo "4,0G /home/toni/Documents/Chez toto"
                echo "1.  **Analyse des modèles Ollama** :"
                echo "Utilisez 'ollama list' pour voir les modèles, et 'ollama rm <model_name>' pour supprimer ceux qui ne sont plus nécessaires."
                echo "2.  **Environnements virtuels Python (venv, miniconda3)** :"
                echo "Supprimez les environnements de projets terminés ou non utilisés."
                echo "Pour venv : 'rm -rf /home/toni/venv'"
                echo "Pour conda : 'conda env remove -n <env_name>'"
                echo "3.  **Dossiers 'connaisance a implenter plus tard' et 'Chez toto'** :"
                echo "Passez en revue ces dossiers pour archiver ou supprimer les données non essentielles."
                echo "4.  **Analyse interactive avec ncdu** :"
                if command -v ncdu &> /dev/null; then
                    if confirm_action "Voulez-vous lancer 'ncdu /home/toni' pour une analyse interactive de l'espace disque ?"; then
                        execute_command "Lancement de ncdu" "ncdu /home/toni"
                    else
                        echo "Analyse ncdu ignorée."
                    fi
                else
                    echo "ncdu n'est pas installé. Veuillez l'installer via la section 'INSTALLATION ET CONFIGURATION DES OUTILS'."
                fi
                ;;
            3) # Nettoyage des caches système
                echo -e "\n--- 3.3. Nettoyage des caches système (APT, vignettes) ---"
                if confirm_action "Voulez-vous nettoyer le cache des paquets APT ?"; then
                    execute_command "Nettoyage du cache APT" "sudo apt clean"
                else
                    echo "Nettoyage du cache APT ignoré."
                fi
                if confirm_action "Voulez-vous nettoyer le cache des vignettes (peut libérer de l'espace) ?"; then
                    execute_command "Nettoyage du cache des vignettes" "rm -rf ~/.cache/thumbnails/*"
                else
                    echo "Nettoyage du cache des vignettes ignoré."
                fi
                ;;
            4) # Optimisation SSD (noatime)
                echo -e "\n--- 3.4. Optimisation des paramètres du noyau pour les SSD (noatime) ---"
                if ! grep -q "noatime" /etc/fstab && ! grep -q "relatime" /etc/fstab; then
                    echo "L'option 'noatime' ou 'relatime' n'est pas configurée dans /etc/fstab pour votre SSD."
                    if confirm_action "Voulez-vous ajouter 'noatime' à la partition racine de votre SSD (/dev/sda2) ? (Cela réduit les écritures et prolonge la durée de vie du SSD. Nécessite un redémarrage.)"; then
                        execute_command "Ajout de noatime à /etc/fstab" "sudo sed -i 's/errors=remount-ro/errors=remount-ro,noatime/' /etc/fstab"
                        echo "L'option 'noatime' a été ajoutée. Veuillez redémarrer pour que les changements prennent effet."
                    else
                        echo "Modification de /etc/fstab ignorée."
                    fi
                else
                    echo "L'option 'noatime' ou 'relatime' est déjà configurée dans /etc/fstab. Excellent."
                fi
                ;;
            0) break ;;
        esac
        echo -e "\nAppuyez sur Entrée pour continuer..."
        read -r
    done
}

# ==============================================================================
# [ 4/6 ] VISION & AUDIT STRATÉGIQUE - MISE EN ŒUVRE AVANCÉE
# ==============================================================================
handle_advanced_hardening() {
    while true; do
        display_menu "VISION & AUDIT STRATÉGIQUE - MISE EN ŒUVRE AVANCÉE" \
            "1. Durcissement du noyau (Kernel Hardening)" \
            "2. Gestion des mises à jour automatiques (unattended-upgrades)" \
            "3. Audit des permissions de fichiers sensibles" \
            "4. Optimisation du CPU Scaling Governor" \
            "5. Préchargement des applications (Preload)" \
            "6. Nettoyage des fichiers temporaires (tmpwatch)" \
            "7. Audit des journaux (Logwatch)" \
            "8. Vérification de l'intégrité des binaires (debsums)" \
            "9. Sécurité des conteneurs Docker" \
            "10. Surveillance des tentatives de connexion échouées (Fail2ban)" \
            "11. Utilisation d'AppArmor/SELinux" \
            "12. Audit des services réseau (ports en écoute)" \
            "13. Utilisation de zram pour le swap compressé" \
            "14. Gestion de l'énergie (TLP/PowerTOP)" \
            "15. Utilisation de fzf pour le terminal" \
            "16. Virtualisation avancée (KVM/QEMU)" \
            "17. Utilisation de apt-listbugs"
        local choice=$?

        case $choice in
            1) # Durcissement du noyau
                echo -e "\n--- 4.1. Durcissement du noyau (Kernel Hardening) ---"
                execute_command "Vérification des paramètres sysctl de sécurité" "sysctl fs.protected_hardlinks fs.protected_symlinks kernel.randomize_va_space kernel.yama.ptrace_scope"
                if sysctl kernel.yama.ptrace_scope | grep -q "kernel.yama.ptrace_scope = 0"; then
                    if confirm_action "Voulez-vous activer 'kernel.yama.ptrace_scope = 1' pour renforcer l'isolation des processus ?"; then
                        execute_command "Activation de kernel.yama.ptrace_scope" "echo \"kernel.yama.ptrace_scope = 1\" | sudo tee -a /etc/sysctl.d/99-sysctl.conf > /dev/null"
                        execute_command "Application des paramètres sysctl" "sudo sysctl -p"
                        echo "kernel.yama.ptrace_scope activé. Redémarrez pour une application complète si nécessaire."
                    else
                        echo "Activation de kernel.yama.ptrace_scope ignorée."
                    fi
                else
                    echo "kernel.yama.ptrace_scope est déjà activé ou configuré."
                fi
                ;;
            2) # unattended-upgrades
                echo -e "\n--- 4.2. Gestion des mises à jour automatiques (unattended-upgrades) ---"
                if ! dpkg -s unattended-upgrades &> /dev/null; then
                    if confirm_action "unattended-upgrades n'est pas installé. L'installer ?"; then
                        execute_command "Installation de unattended-upgrades" "sudo apt install -y unattended-upgrades"
                    fi
                fi
                if dpkg -s unattended-upgrades &> /dev/null; then
                    if confirm_action "Voulez-vous activer et configurer 'unattended-upgrades' pour les mises à jour de sécurité ?"; then
                        execute_command "Configuration de unattended-upgrades" "sudo dpkg-reconfigure --priority=low unattended-upgrades"
                        echo "unattended-upgrades configuré. Vérifiez le fichier '/etc/apt/apt.conf.d/20auto-upgrades' pour les détails."
                    else
                        echo "Configuration de unattended-upgrades ignorée."
                    fi
                fi
                ;;
            3) # Permissions fichiers sensibles
                echo -e "\n--- 4.3. Audit des permissions de fichiers sensibles ---"
                execute_command "Vérification des permissions des répertoires sensibles" "ls -ld /etc /var/log /home"
                echo "Il est crucial que ces répertoires aient des permissions restrictives (ex: /etc et /var/log souvent 755, /home souvent 755 ou 700 pour les répertoires utilisateurs)."
                execute_command "Recherche de fichiers 'world-writable' dans /etc" "find /etc -type f -perm /002 -ls"
                ;;
            4) # CPU Scaling Governor
                echo -e "\n--- 4.4. Optimisation du CPU Scaling Governor ---"
                if command -v cpufreq-info &> /dev/null; then
                    execute_command "État actuel du CPU Scaling Governor" "cpufreq-info"
                    echo "Les gouverneurs courants sont 'powersave' (économie d'énergie) et 'performance' (puissance maximale)."
                    if confirm_action "Voulez-vous changer temporairement le gouverneur en 'performance' ?"; then
                        execute_command "Changement du gouverneur en performance" "sudo cpufreq-set -g performance"
                        execute_command "Vérification après changement" "cpufreq-info"
                    fi
                    echo "Pour un changement persistant, utilisez TLP (si installé) ou configurez un service systemd personnalisé."
                else
                    echo "cpufrequtils n'est pas installé. Veuillez l'installer via la section 'INSTALLATION ET CONFIGURATION DES OUTILS'."
                fi
                ;;
            5) # Preload
                echo -e "\n--- 4.5. Préchargement des applications (Preload) ---"
                if command -v preload &> /dev/null; then
                    execute_command "Statut du service preload" "systemctl status preload.service --no-pager"
                    if ! systemctl is-enabled preload.service &> /dev/null; then
                        if confirm_action "Le service preload n'est pas activé. L'activer ?"; then
                            execute_command "Activation de preload.service" "sudo systemctl enable preload.service --now"
                        fi
                    fi
                else
                    echo "Preload n'est pas installé. Veuillez l'installer via la section 'INSTALLATION ET CONFIGURATION DES OUTILS'."
                fi
                ;;
            6) # tmpwatch
                echo -e "\n--- 4.6. Nettoyage des fichiers temporaires (tmpwatch) ---"
                if command -v tmpwatch &> /dev/null; then
                    echo "tmpwatch est installé. Il peut être utilisé pour nettoyer les répertoires temporaires."
                    echo "Exemple : 'sudo tmpwatch 7d /tmp' (supprime les fichiers de plus de 7 jours dans /tmp)."
                    if confirm_action "Voulez-vous exécuter 'sudo tmpwatch 7d /tmp' maintenant ?"; then
                        execute_command "Nettoyage de /tmp avec tmpwatch" "sudo tmpwatch 7d /tmp"
                    fi
                else
                    echo "tmpwatch n'est pas installé. Veuillez l'installer via la section 'INSTALLATION ET CONFIGURATION DES OUTILS'."
                fi
                ;;
            7) # Logwatch
                echo -e "\n--- 4.7. Audit des journaux (Logwatch) ---"
                if command -v logwatch &> /dev/null; then
                    echo "Logwatch est installé. Il génère des rapports quotidiens sur l'activité de votre système."
                    echo "Configurez-le via '/etc/logwatch/conf/logwatch.conf' et '/etc/logwatch/conf/services/'."
                    if confirm_action "Voulez-vous générer un rapport Logwatch maintenant (peut être long) ?"; then
                        execute_command "Génération rapport Logwatch" "sudo logwatch --detail High --range today"
                    fi
                else
                    echo "Logwatch n'est pas installé. Veuillez l'installer via la section 'INSTALLATION ET CONFIGURATION DES OUTILS'."
                fi
                ;;
            8) # debsums
                echo -e "\n--- 4.8. Vérification de l'intégrité des binaires (debsums) ---"
                if command -v debsums &> /dev/null; then
                    echo "debsums est installé. Exécutez 'sudo debsums -c' pour vérifier l'intégrité des paquets installés."
                    echo "Ceci peut prendre un certain temps et lister les fichiers modifiés (ex: fichiers de configuration)."
                    if confirm_action "Voulez-vous exécuter 'sudo debsums -c' maintenant ?"; then
                        execute_command "Exécution de debsums" "sudo debsums -c"
                    fi
                else
                    echo "debsums n'est pas installé. Veuillez l'installer via la section 'INSTALLATION ET CONFIGURATION DES OUTILS'."
                fi
                ;;
            9) # Docker Security
                echo -e "\n--- 4.9. Sécurité des conteneurs Docker ---"
                echo "Appliquer les meilleures pratiques Docker (non-root users, scan d'images, limites de ressources)."
                if confirm_action "Voulez-vous exécuter 'docker system prune -a' pour nettoyer les ressources Docker inutilisées (images, conteneurs arrêtés, volumes non utilisés) ?"; then
                    execute_command "Nettoyage Docker" "sudo docker system prune -a"
                fi
                ;;
            10) # Fail2ban
                echo -e "\n--- 4.10. Surveillance des tentatives de connexion échouées (Fail2ban) ---"
                if command -v fail2ban-client &> /dev/null; then
                    execute_command "Statut du service Fail2ban" "sudo systemctl status fail2ban.service --no-pager"
                    if ! systemctl is-enabled fail2ban.service &> /dev/null; then
                        if confirm_action "Le service Fail2ban n'est pas activé. L'activer ?"; then
                            execute_command "Activation de fail2ban.service" "sudo systemctl enable fail2ban.service --now"
                        fi
                    fi
                    echo "Configurez Fail2ban via '/etc/fail2ban/jail.local'."
                else
                    echo "Fail2ban n'est pas installé. Veuillez l'installer via la section 'INSTALLATION ET CONFIGURATION DES OUTILS'."
                fi
                ;;
            11) # AppArmor/SELinux
                echo -e "\n--- 4.11. Utilisation d'AppArmor/SELinux ---"
                echo "AppArmor est par défaut sur Ubuntu. Vérifiez son statut :"
                execute_command "Statut AppArmor" "sudo aa-status"
                echo "Apprenez à créer ou ajuster des profils si vous avez des applications spécifiques."
                ;;
            12) # Audit services réseau
                echo -e "\n--- 4.12. Audit des services réseau (ports en écoute) ---"
                if command -v ss &> /dev/null; then
                    execute_command "Ports TCP en écoute" "sudo ss -tuln | grep LISTEN"
                    execute_command "Ports UDP en écoute" "sudo ss -uuln"
                else
                    echo "L'outil 'ss' n'est pas trouvé. Veuillez installer 'iproute2' si vous souhaitez l'utiliser."
                fi
                echo "Assurez-vous que seuls les services nécessaires sont exposés."
                ;;
            13) # zram
                echo -e "\n--- 4.13. Utilisation de zram pour le swap compressé ---"
                if command -v zramctl &> /dev/null; then
                    execute_command "Statut de zram" "zramctl"
                    if ! systemctl is-enabled zramswap.service &> /dev/null; then
                        if confirm_action "Le service zramswap n'est pas activé. L'activer ?"; then
                            execute_command "Activation de zramswap.service" "sudo systemctl enable zramswap.service --now"
                        fi
                    fi
                    echo "Configurez zram via '/etc/default/zramswap'."
                else
                    echo "zram-tools n'est pas installé. Veuillez l'installer via la section 'INSTALLATION ET CONFIGURATION DES OUTILS'."
                fi
                ;;
            14) # TLP/PowerTOP
                echo -e "\n--- 4.14. Gestion de l'énergie (TLP/PowerTOP) ---"
                if command -v tlp &> /dev/null; then
                    echo "TLP est installé et devrait gérer l'énergie. Pour des rapports détaillés : 'sudo tlp-stat'."
                elif command -v powertop &> /dev/null; then
                    echo "PowerTOP est installé. Pour optimiser : 'sudo powertop --auto-tune'."
                else
                    echo "Aucun outil de gestion d'énergie avancé n'est installé. Veuillez installer TLP ou PowerTOP via la section 'INSTALLATION ET CONFIGURATION DES OUTILS'."
                fi
                ;;
            15) # fzf
                echo -e "\n--- 4.15. Utilisation de fzf pour une meilleure productivité du terminal ---"
                if command -v fzf &> /dev/null; then
                    echo "fzf est installé. C'est un outil de recherche floue interactif pour le terminal."
                    echo "Intégrez-le à votre shell (bash/zsh) pour des recherches d'historique, de fichiers, etc. plus rapides."
                    echo "Consultez la documentation de fzf pour l'intégration."
                else
                    echo "fzf n'est pas installé. Veuillez l'installer via la section 'INSTALLATION ET CONFIGURATION DES OUTILS'."
                fi
                ;;
            16) # KVM/QEMU
                echo -e "\n--- 4.16. Virtualisation avancée (KVM/QEMU) ---"
                if command -v kvm &> /dev/null; then
                    echo "KVM/QEMU est installé. Pour gérer les VMs, utilisez 'virt-manager'."
                    echo "Assurez-vous que votre utilisateur est dans les groupes 'libvirt' et 'kvm'."
                    execute_command "Vérification des groupes de l'utilisateur" "groups toni"
                else
                    echo "KVM/QEMU n'est pas installé. Veuillez l'installer via la section 'INSTALLATION ET CONFIGURATION DES OUTILS'."
                fi
                ;;
            17) # apt-listbugs
                echo -e "\n--- 4.17. Utilisation de apt-listbugs ---"
                if dpkg -s apt-listbugs &> /dev/null; then
                    echo "apt-listbugs est installé. Il vous alertera des bugs critiques lors des mises à jour."
                else
                    echo "apt-listbugs n'est pas installé. Veuillez l'installer via la section 'INSTALLATION ET CONFIGURATION DES OUTILS'."
                fi
                ;;
            0) break ;;
        esac
        echo -e "\nAppuyez sur Entrée pour continuer..."
        read -r
    done
}

# ==============================================================================
# [ 5/6 ] INTÉGRATION D'OUTILS D'INTELLIGENCE ARTIFICIELLE GRATUITS ET OPTIMISÉS
# ==============================================================================
handle_ai_integration() {
    echo -e "\n=============================================================================="
    echo -e "[ 5/6 ] INTÉGRATION D'OUTILS D'INTELLIGENCE ARTIFICIELLE GRATUITS ET OPTIMISÉS"
    echo -e "=============================================================================="
    echo "Votre PC est une excellente base pour l'IA locale, grâce à votre CPU Intel et vos 32 GiB de RAM."
    echo "Nous allons explorer l'intégration d'outils d'IA gratuits et optimisés pour votre configuration."

    while true; do
        display_menu "CHOIX DES OUTILS IA À INTÉGRER" \
            "1. Ollama : Gestionnaire de modèles LLM locaux (déjà installé)" \
            "2. Llama.cpp : Exécution de LLM sur CPU" \
            "3. Jupyter Notebooks : Environnement de développement IA interactif" \
            "4. Optimisation CPU pour l'IA (numactl, taskset)" \
            "5. Vision : Projets IA locaux pour votre PC"
        local choice=$?

        case $choice in
            1) # Ollama
                echo -e "\n--- 5.1. Ollama : Gestionnaire de modèles LLM locaux ---"
                if command -v ollama &> /dev/null; then
                    echo "Ollama est déjà installé. C'est votre porte d'entrée vers les LLM locaux."
                    execute_command "Liste des modèles Ollama installés" "ollama list"
                    echo "Votre dossier '.ollama/models' contient 9.0G de modèles, ce qui est significatif."
                    echo "1.  **Télécharger un nouveau modèle (ex: Mistral)** :"
                    echo "   Exemple : 'ollama pull mistral'"
                    if confirm_action "Voulez-vous télécharger le modèle 'mistral' (environ 4.1GB) maintenant ?"; then
                        execute_command "Téléchargement de Mistral" "ollama pull mistral"
                    fi
                    echo "2.  **Exécuter un modèle** :"
                    echo "   Exemple : 'ollama run mistral \"Quelle est la capitale de la France ?\"'"
                    echo "   Vous pouvez interagir en mode conversationnel après 'ollama run mistral'."
                    if confirm_action "Voulez-vous lancer une conversation avec 'mistral' (tapez votre question, puis Ctrl+D pour quitter) ?"; then
                        execute_command "Lancement de Mistral" "ollama run mistral"
                    fi
                    echo "3.  **Supprimer un modèle** :"
                    echo "   Exemple : 'ollama rm mistral' (pour libérer de l'espace)."
                    echo "4.  **Utilisation de l'API Ollama** :"
                    echo "   Ollama expose une API locale (par défaut sur http://localhost:11434) pour intégrer les LLM à vos applications."
                    echo "   Vous pouvez l'utiliser avec Python, JavaScript, etc."
                else
                    echo "Ollama n'est pas installé. Il est fortement recommandé pour l'IA locale."
                    if confirm_action "Voulez-vous installer Ollama maintenant ?"; then
                        execute_command "Installation d'Ollama" "curl -fsSL https://ollama.com/install.sh | sh"
                        echo "Ollama installé. Redémarrez votre terminal et relancez cette section."
                    fi
                fi
                ;;
            2) # Llama.cpp
                echo -e "\n--- 5.2. Llama.cpp : Exécution de LLM sur CPU ---"
                echo "Llama.cpp est une implémentation C/C++ légère pour exécuter des modèles LLM (comme Llama, Mistral) sur CPU."
                echo "Il est souvent utilisé comme backend pour Ollama ou directement pour plus de contrôle."
                echo "1.  **Installation des dépendances de compilation** :"
                if ! dpkg -s build-essential cmake &> /dev/null; then
                    if confirm_action "Voulez-vous installer les dépendances de compilation (build-essential, cmake) ?"; then
                        execute_command "Installation des dépendances" "sudo apt install -y build-essential cmake"
                    fi
                fi
                echo "2.  **Cloner le dépôt et compiler Llama.cpp** :"
                if [ ! -d "$HOME/llama.cpp" ]; then
                    if confirm_action "Voulez-vous cloner llama.cpp dans votre répertoire personnel et le compiler ?"; then
                        execute_command "Clonage de llama.cpp" "git clone https://github.com/ggerganov/llama.cpp.git $HOME/llama.cpp"
                        execute_command "Compilation de llama.cpp" "cd $HOME/llama.cpp && make"
                        echo "Llama.cpp compilé. Vous pouvez maintenant télécharger des modèles GGUF et les exécuter."
                        echo "Exemple : Téléchargez un modèle GGUF (ex: Mistral 7B Q4_K_M) depuis Hugging Face et placez-le dans '$HOME/llama.cpp/models'."
                        echo "Exécution : '$HOME/llama.cpp/main -m $HOME/llama.cpp/models/mistral-7b-v0.2.Q4_K_M.gguf -p \"Bonjour, comment allez-vous ?\"'"
                    fi
                else
                    echo "Llama.cpp est déjà cloné dans '$HOME/llama.cpp'."
                    if confirm_action "Voulez-vous recompiler llama.cpp (pour les mises à jour) ?"; then
                        execute_command "Recompilation de llama.cpp" "cd $HOME/llama.cpp && make clean && make"
                    fi
                fi
                ;;
            3) # Jupyter Notebooks
                echo -e "\n--- 5.3. Jupyter Notebooks : Environnement de développement IA interactif ---"
                echo "Jupyter est idéal pour expérimenter avec l'IA, visualiser des données et écrire du code Python interactif."
                echo "Vous avez déjà Python et Conda, ce qui est parfait."
                if ! command -v jupyter &> /dev/null; then
                    if confirm_action "Voulez-vous installer Jupyter Notebook via pip (dans votre environnement actif) ?"; then
                        execute_command "Installation de Jupyter" "pip install notebook"
                        echo "Jupyter Notebook installé. Pour le lancer : 'jupyter notebook'."
                        echo "Il s'ouvrira dans votre navigateur web."
                    fi
                else
                    echo "Jupyter Notebook est déjà installé."
                fi
                if confirm_action "Voulez-vous lancer Jupyter Notebook maintenant ?"; then
                    execute_command "Lancement de Jupyter Notebook" "jupyter notebook"
                fi
                ;;
            4) # Optimisation CPU pour l'IA
                echo -e "\n--- 5.4. Optimisation CPU pour l'IA (numactl, taskset) ---"
                echo "Pour maximiser les performances des LLM sur CPU, l'optimisation de l'utilisation des cœurs et de la mémoire est cruciale."
                echo "Votre CPU a 2 cœurs / 4 threads."
                echo "1.  **numactl** : Pour les systèmes NUMA, mais peut aider à l'allocation mémoire."
                if ! command -v numactl &> /dev/null; then
                    if confirm_action "Voulez-vous installer numactl ?"; then
                        execute_command "Installation de numactl" "sudo apt install -y numactl"
                    fi
                else
                    echo "numactl est déjà installé."
                fi
                echo "2.  **taskset** : Pour assigner un processus à des cœurs CPU spécifiques."
                echo "   Exemple : 'taskset -c 0-3 ollama run mistral \"...\"' (utilise les 4 threads logiques)."
                echo "   Cela peut améliorer la cohérence des performances en évitant les migrations de processus."
                echo "3.  **Quantification des modèles** : Ollama et Llama.cpp utilisent des modèles quantifiés (Q4, Q5, Q8) qui réduisent la taille et la consommation de RAM/CPU au détriment d'une légère perte de précision."
                echo "   Assurez-vous de choisir des modèles avec une quantification adaptée à votre RAM (32 GiB est excellent)."
                echo "4.  **Paramètres de compilation (Llama.cpp)** : Lors de la compilation de Llama.cpp, des flags comme '-march=native' ou des options spécifiques à Intel (AVX2, FMA) sont activés par défaut pour maximiser les performances CPU."
                ;;
            5) # Vision : Projets IA locaux
                echo -e "\n--- 5.5. Vision : Projets IA locaux pour votre PC ---"
                echo "Voici des idées pour exploiter l'IA sur votre machine, en mode 'God Ultimate IA free' :"
                echo "1.  **Assistant Personnel IA Local et Privé** :"
                echo "    Utilisez Ollama pour un chatbot local qui peut répondre à vos questions, résumer des documents locaux (via RAG - Retrieval Augmented Generation), et même contrôler des aspects de votre système via des scripts."
                echo "    Exemple : 'ollama run llama3 \"Écris un script shell pour nettoyer mon dossier Téléchargements.\""
                echo "2.  **Génération de Code et Complétion Intelligente** :"
                echo "    Intégrez un LLM local à votre éditeur de code (VS Code via des extensions) pour la complétion de code, la génération de fonctions, la détection de bugs ou l'explication de code."
                echo "3.  **Analyse de Données et Rapports Automatisés** :"
                echo "    Utilisez Jupyter avec des LLM locaux pour analyser de grands ensembles de données, générer des rapports, ou extraire des informations clés de documents non structurés."
                echo "4.  **Création de Contenu (Texte, Idées)** :"
                echo "    Générez des idées de projets, des brouillons d'e-mails, des articles de blog, ou des scripts pour vos vidéos, tout en gardant le contrôle total sur la confidentialité."
                echo "5.  **Base de Connaissances Personnelle Intelligente** :"
                echo "    Créez un système RAG qui interroge vos propres documents (notes, livres, PDFs) en utilisant un LLM local, transformant votre PC en un 'second cerveau' intelligent."
                echo "6.  **Apprentissage et Tutorat IA** :"
                echo "    Utilisez un LLM local comme tuteur pour apprendre de nouvelles compétences, expliquer des concepts complexes ou pratiquer une langue."
                echo "7.  **Automatisation Système Intelligente** :"
                echo "    Développez des scripts Python qui utilisent l'API Ollama pour automatiser des tâches complexes, comme la classification de fichiers, la réponse à des e-mails ou la gestion de votre calendrier."
                echo "8.  **Création Artistique (Texte-Image sur CPU)** :"
                echo "    Bien que lent sur CPU, vous pouvez expérimenter avec des modèles de génération d'images (comme Stable Diffusion via 'InvokeAI' ou 'Automatic1111' avec des optimisations CPU) pour créer des visuels uniques."
                echo "9.  **Vie Privée et Contrôle** :"
                echo "    L'avantage majeur de l'IA locale est la confidentialité. Vos données ne quittent jamais votre machine, vous gardez un contrôle total sur l'IA."
                echo "10. **Optimisation Continue de l'IA Locale** :"
                echo "    Explorez des techniques comme la quantification, le fine-tuning de petits modèles sur vos propres données, et l'utilisation de frameworks comme ONNX Runtime pour accélérer l'inférence."
                ;;
            0) break ;;
        esac
        echo -e "\nAppuyez sur Entrée pour continuer..."
        read -r
    done
}


# ==============================================================================
# [ 6/6 ] VISION STRATÉGIQUE ET ÉVOLUTION (Recommandations Futures)
# ==============================================================================
handle_strategic_vision() {
    echo -e "\n=============================================================================="
    echo -e "[ 6/6 ] VISION STRATÉGIQUE ET ÉVOLUTION (Recommandations Futures)"
    echo -e "=============================================================================="
    echo "Cette section présente des recommandations pour l'avenir de votre système, pour une optimisation continue et une vision à long terme."
    echo "Ces points ne sont pas interactifs dans ce script, mais sont des pistes de réflexion et d'action."

    echo -e "\n--- 6.1. Audit et Hardening du Système (Suite des 20 points) ---"
    echo "1.  **Authentification forte (2FA/MFA)** : Envisager l'activation de l'authentification à deux facteurs pour les connexions SSH ou l'accès au système (ex: `libpam-google-authenticator`)."
    echo "2.  **Stratégie de sauvegarde (Backup Strategy)** : Mettre en place une solution de sauvegarde robuste et automatisée pour vos données critiques (ex: BorgBackup, rsync vers un NAS/cloud). C'est crucial."
    echo "3.  **Chiffrement du disque (Disk Encryption)** : Si ce n'est pas déjà fait, envisager le chiffrement complet du disque pour protéger les données en cas de vol physique (LUKS)."
    echo "4.  **Gestion des secrets** : Pour le développement, utiliser des outils de gestion de secrets (ex: HashiCorp Vault, `pass`) plutôt que de stocker les identifiants en clair."
    echo "5.  **Politique de mots de passe** : Appliquer une politique de mots de passe forts et renouvelés régulièrement. Utilisez un gestionnaire de mots de passe."
    echo "6.  **Désactivation des services inutiles** : Examiner la liste complète des services systemd ('systemctl list-unit-files --type=service') et désactiver ceux qui ne sont absolument pas nécessaires."
    echo "7.  **Surveillance de l'intégrité des fichiers (FIM)** : Utiliser des outils comme AIDE ou Tripwire pour détecter les modifications non autorisées des fichiers système."
    echo "8.  **Sécurité du navigateur** : Utiliser des extensions de sécurité (uBlock Origin, HTTPS Everywhere) et configurer les navigateurs pour une confidentialité maximale."
    echo "9.  **VPN/Proxy** : Utiliser un VPN pour les connexions non sécurisées ou pour masquer votre adresse IP publique."
    echo "10. **Analyse des vulnérabilités (Vulnerability Scanning)** : Utiliser des outils comme Lynis ou OpenVAS pour scanner le système à la recherche de vulnérabilités connues."
    echo "11. **Plan de réponse aux incidents** : Avoir une procédure claire en cas d'incident de sécurité (compromission, perte de données)."
    echo "12. **Gestion des versions de code** : Utiliser Git de manière rigoureuse pour tous vos projets, avec des dépôts distants (GitHub, GitLab)."
    echo "13. **Conteneurisation des environnements de développement** : Utiliser Docker ou Podman pour isoler les projets de développement et leurs dépendances, garantissant la reproductibilité."

    echo -e "\n--- 6.2. Optimisation des Performances et de l'Expérience Utilisateur (Suite des 15 points) ---"
    echo "1.  **Nettoyage des caches système** : Purger régulièrement les caches APT ('sudo apt clean'), les caches des vignettes ('rm -rf ~/.cache/thumbnails/*')."
    echo "2.  **Gestion des tâches Cron** : Examiner les tâches cron de l'utilisateur ('crontab -l') et du système (`/etc/cron.*`) pour s'assurer qu'elles sont pertinentes et optimisées."
    echo "3.  **Optimisation du démarrage des applications** : Réduire le nombre d'applications lancées au démarrage de la session KDE Plasma (Paramètres Système -> Démarrage et Arrêt -> Démarrage automatique)."
    echo "4.  **Optimisation des paramètres du navigateur** : Configurer Chrome/Opera pour une meilleure performance et une consommation de RAM réduite (ex: suspension d'onglets, désactivation de l'accélération matérielle si problèmes)."
    echo "5.  **Mise à jour des pilotes graphiques Intel** : S'assurer que les pilotes i915 sont à jour via les mises à jour du noyau pour de meilleures performances graphiques. Surveillez les logs pour les erreurs i915."
    echo "6.  **Optimisation des services Docker** : Configurer Docker pour utiliser des pilotes de stockage optimisés et limiter les ressources des conteneurs."
    echo "7.  **Gestion des polices** : Supprimer les polices inutilisées pour accélérer le rendu des applications et libérer de l'espace."
    echo "8.  **Personnalisation de l'environnement de bureau** : Désactiver les effets visuels lourds de KDE Plasma si les performances sont un souci (Paramètres Système -> Effets de bureau)."

    echo -e "\n--- 6.3. Vision Stratégique et Évolution (Suite des 15 points) ---"
    echo "1.  **Automatisation des tâches d'administration** : Développer des scripts Ansible ou des playbooks pour automatiser les configurations et les déploiements sur votre machine."
    echo "2.  **Intégration CI/CD locale** : Mettre en place un pipeline CI/CD léger (ex: Gitea Actions, Drone CI) pour vos projets de développement personnels."
    echo "3.  **Surveillance proactive** : Utiliser des outils comme Prometheus et Grafana (en local) pour visualiser les métriques de performance du système en temps réel."
    echo "4.  **Apprentissage continu** : Se tenir informé des dernières avancées en matière de sécurité Linux, d'optimisation des performances et des outils de développement."
    echo "5.  **Contribution Open Source** : Participer à des projets open source pour améliorer vos compétences et contribuer à la communauté."
    echo "6.  **Documentation personnelle** : Maintenir une documentation de votre configuration système, de vos scripts et de vos solutions aux problèmes rencontrés."
    echo "7.  **Évaluation des besoins matériels futurs** : Planifier les futures mises à niveau matérielles (ex: plus de RAM, un SSD plus grand/NVMe si possible, une carte graphique dédiée si les besoins évoluent)."
    echo "8.  **Considérations sur le cloud** : Évaluer l'intégration avec des services cloud pour le stockage, le calcul ou le déploiement de vos applications."
    echo "9.  **Optimisation des flux de travail (Workflow Optimization)** : Analyser vos habitudes de travail et identifier les goulots d'étranglement pour les automatiser ou les rationaliser."
    echo "10. **Sécurité physique** : Verrouiller physiquement l'ordinateur, utiliser un mot de passe BIOS/UEFI, et protéger l'accès physique."
    echo "11. **Gestion des identités et accès (IAM)** : Pour des environnements plus complexes, envisager des solutions IAM même pour un usage personnel."
    echo "12. **Veille technologique** : Suivre les blogs techniques, les conférences et les communautés pour rester à la pointe des technologies."
    echo "13. **Gestion des règles Udev personnalisées** : Pour des problèmes matériels spécifiques (comme le rétroéclairage ou certains périphériques USB), la création de règles Udev personnalisées peut offrir une solution plus robuste."

    echo -e "\nAppuyez sur Entrée pour revenir au menu principal..."
    read -r
}


# ==============================================================================
# BOUCLE PRINCIPALE DU SCRIPT
# ==============================================================================
main_menu() {
    while true; do
        echo -e "\n=============================================================================="
        echo -e "[ MENU PRINCIPAL GOD MODE++++ - L'ULTIME ÉVOLUTION ]"
        echo -e "=============================================================================="
        display_menu "Choisissez une section pour l'analyse et l'optimisation" \
            "1. Vérification Complète des Actions Précédentes" \
            "2. Installation et Configuration des Outils Manquants" \
            "3. Optimisations & Améliorations Générales" \
            "4. Vision & Audit Stratégique - Mise en Œuvre Avancée" \
            "5. Intégration d'Outils d'Intelligence Artificielle Gratuits et Optimisés" \
            "6. Vision Stratégique et Évolution (Recommandations Futures)"
        local choice=$?

        case $choice in
            1) verify_previous_actions ;;
            2) handle_tool_installation ;;
            3) handle_general_optimizations ;;
            4) handle_advanced_hardening ;;
            5) handle_ai_integration ;;
            6) handle_strategic_vision ;;
            0)
                echo -e "\n=============================================================================="
                echo -e "[ FIN DU RAPPORT GOD MODE++++ - PARTIE 6 ]"
                echo -e "=============================================================================="
                echo "Félicitations, Toni ! Vous avez parcouru un chemin considérable dans l'optimisation et la sécurisation de votre système."
                echo "L'intégration de l'IA locale ouvre de nouvelles perspectives pour votre productivité et votre créativité."
                echo "Un redémarrage est fortement recommandé pour que tous les changements prennent pleinement effet."
                echo "Votre PC est maintenant une machine d'exception, prête pour l'avenir. La perfection est un voyage, pas une destination !"
                exit 0
                ;;
        esac
    done
}

# Lancement du menu principal
main_menu
