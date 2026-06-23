import os
from cryptography.fernet import Fernet
import git

def gerer_cle_secrete():
    """Charge la clé existante ou en génère une nouvelle si elle n'existe pas."""
    fichier_cle = "cle_secrete.key"
    if os.path.exists(fichier_cle):
        with open(fichier_cle, "rb") as f:
            return f.read()
    else:
        cle = Fernet.generate_key()
        with open(fichier_cle, "wb") as f:
            f.write(cle)
        print("[INFO] Nouvelle clé de sécurité générée et sauvegardée.")
        return cle

def chiffrer_fichier(chemin_fichier, cle):
    """Chiffre un fichier utilisateur, le place dans Git et supprime l'original."""
    print(f"\n--- Chiffrement de {os.path.basename(chemin_fichier)} ---")
    try:
        fernet = Fernet(cle)
        with open(chemin_fichier, 'rb') as f:
            donnees = f.read()
            
        donnees_chiffrees = fernet.encrypt(donnees)
        
        # Redirection du fichier chiffré vers le répertoire courant (le dépôt Git)
        nom_fichier = os.path.basename(chemin_fichier)
        
        # FIX: We use just the filename without './' to prevent GitHub 'hasDot' rejection errors
        chemin_chiffre = f"{nom_fichier}.enc"
        
        with open(chemin_chiffre, 'wb') as f:
            f.write(donnees_chiffrees)
            
        print(f"Succès : Fichier chiffré créé dans le dépôt Git -> {chemin_chiffre}")
        
        # Suppression stricte du fichier en clair
        os.remove(chemin_fichier)
        print(f"Sécurité : Le fichier original en clair a été supprimé.")
        
        return chemin_chiffre
    except Exception as e:
        print(f"Erreur lors du chiffrement : {e}")
        return None

def dechiffrer_fichier(chemin_fichier_chiffre, cle):
    """Restaure un fichier chiffré dans son format d'origine."""
    print(f"\n--- Déchiffrement de {os.path.basename(chemin_fichier_chiffre)} ---")
    try:
        fernet = Fernet(cle)
        with open(chemin_fichier_chiffre, 'rb') as f:
            donnees_chiffrees = f.read()
            
        donnees_claires = fernet.decrypt(donnees_chiffrees)
        
        # Retrouver l'extension d'origine (ex: .csv ou .docx)
        chemin_base = chemin_fichier_chiffre.replace('.enc', '')
        nom, extension = os.path.splitext(chemin_base)
        chemin_restaure = f"{nom}_restaure{extension}"
        
        with open(chemin_restaure, 'wb') as f:
            f.write(donnees_claires)
            
        print(f"Succès : Fichier restauré avec succès -> {chemin_restaure}")
        return chemin_restaure
    except Exception as e:
        print(f"Erreur lors du déchiffrement : {e}")
        return None

def publier_sur_git(chemin_fichier_chiffre):
    """Automatise le commit et le push du fichier sécurisé."""
    print(f"\n--- Publication Git de {os.path.basename(chemin_fichier_chiffre)} ---")
    try:
        repo = git.Repo('.')
        repo.index.add([chemin_fichier_chiffre])
        
        message_commit = f"SecOps: Ajout sécurisé de {os.path.basename(chemin_fichier_chiffre)}"
        repo.index.commit(message_commit)
        print(f"Succès : Commit validé dans l'historique -> '{message_commit}'.")
        
        if repo.remotes:
            print("Synchronisation distante en cours (git push)...")
            resultats_push = repo.remotes.origin.push()
            
            # Vérification stricte des statuts de retour du Push
            erreur_trouvee = False
            for info in resultats_push:
                if info.flags & (git.remote.PushInfo.ERROR | git.remote.PushInfo.REJECTED):
                    erreur_trouvee = True
                    print(f"Échec de l'envoi sur GitHub : {info.summary}")
            
            if not erreur_trouvee:
                print("Succès : Fichier publié en toute sécurité sur le serveur distant !")
            else:
                print("Attention : Le fichier est sécurisé localement, mais l'envoi a échoué.")
        else:
            print("Information : Aucun serveur distant configuré. Sauvegarde locale validée.")
            
        return True
    except Exception as e:
        print(f"Erreur Git critique : {e}")
        return False

# --- POINT D'ENTRÉE DU SCRIPT ---
if __name__ == "__main__":
    print("=========================================")
    print("   Outil SecOps - Version Production     ")
    print("=========================================")
    print("1 : Sécuriser un fichier (Chiffrement + Envoi Git)")
    print("2 : Restaurer un fichier (Déchiffrement local)")
    
    choix = input("\nVotre choix (1 ou 2) : ")
    
    # Chargement automatique de la clé
    cle_symetrique = gerer_cle_secrete()
    
    if choix == '1':
        chemin_utilisateur = input("\nChemin complet du fichier à sécuriser : ").strip('"').strip("'")
        if os.path.exists(chemin_utilisateur):
            fichier_securise = chiffrer_fichier(chemin_utilisateur, cle_symetrique)
            if fichier_securise:
                publier_sur_git(fichier_securise)
                print("\n[OK] Opération terminée. Le fichier est sécurisé sur Git.")
        else:
            print("\nErreur : Le fichier spécifié est introuvable.")
            
    elif choix == '2':
        chemin_utilisateur = input("\nChemin complet du fichier .enc à déchiffrer : ").strip('"').strip("'")
        if os.path.exists(chemin_utilisateur):
            dechiffrer_fichier(chemin_utilisateur, cle_symetrique)
            print("\n[OK] Opération terminée. Le fichier est lisible.")
        else:
            print("\nErreur : Le fichier spécifié est introuvable.")
            
    else:
        print("\nErreur : Choix invalide.")