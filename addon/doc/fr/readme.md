# ffTools

Ensemble d'outils du programme ffmpeg pour le traitement des fichiers multimédias.

[Gerardo Kessler](http://gera.ar/sonido/sobremi.php)  

Basé sur le programme [ffmpeg](https://ffmpeg.org/)  

Téléchargement des fichiers binaires: <https://github.com/yt-dlp/FFmpeg-Builds/wiki/Latest>

Important: Ce module est basé sur  les binaires FF, il est donc fondamental de télécharger ces fichiers. L'extension propose de les télécharger et de les enregistrer au bon endroit, bien que l'utilisateur puisse également le faire en copiant le dossier bin avec les fichiers ffmpeg.exe et ffplay.exe à la racine de l'extension:

    %AppData%\nvda\addons\ffTools\globalPlugins\ffTools

## Commandes de l'extension:

* Prévisualiser le fichier audio ou vidéo focalisé; Non assigné
* Activer les commandes en couche; Non assigné

### Commandes de prévisualisation

Une fois la prévisualisation activée, les commandes suivantes fonctionnent dans la fenêtre de lecture

* Barre d'espace; Mettre en pause  et reprendre la lecture
* Page suivante; Lire dès le début
* Flèche gauche; Recule dans la ligne de temps
* Flèche droite; Avance dans la ligne de temps
* Flèche haut; Augmente le volume de lecture
* Flèche bas; Baisse le volume de lecture
* Échap; Ferme la fenêtre

### Commandes en couche

* f1; Ouvre ce document dans le navigateur par défaut
* f; Active une fenêtre qui permet de modifier le volume, le format et le bitrate du fichier focalisé
* c; Active une fenêtre qui permet de modifier la vitesse, coupez le début et la fin du fichier focalisé
* l; Active une fenêtre de conversion par lots

## Découpe

Lors de l'activation des commandes en couche  et appuyer sur la lettre c, la fenêtre de vitesse et de découpe sont activées.
Si la case à cocher "Modifier la vitesse du fichier" est cochée, seule la liste des pourcentages à sélectionner est affichée.

Sinon,  2 zones d'édition sont disponibles pour sélectionner le début et la fin de la coupe. Si vous souhaitez couper les 10 premières secondes du fichier, la zone d'édition doit être modifiée comme 00:10. Il est important de respecter le format de 2 nombres pour les minutes et 2 pour les secondes.
Dans la zone d'édition pour la coupe finale, l'étiquette verbalise le temps total du fichier, qui sera également reflété dans la valeur du champ.
Pour couper les 10 dernières secondes du fichier, vous devez modifier la zone d'édition en tapant la valeur actuelle avec les secondes soustraites. Si le fichier a une durée de 03:07, il devrait rester 02:57.

### Conversion par lots

Cette option vous permet de convertir tous les fichiers pris en charge par FFMpeg  existant dans un répertoire.

Une fois les commandes en couche activé et que la touche l est appuyée, une fenêtre de dialogue avec les options suivantes est affichée:

* Chemin du dossier: Ici, le chemin du dossier est affiché avec les fichiers.
* Parcourir: Bouton qui ouvre le dialogue typique de Windows pour rechercher un dossier avec des fichiers à convertir.
* Format à convertir: Liste des formats de sortie disponibles.
* Normaliser le volume audio: Il permet de normaliser les audios à un niveau sonore objectif de -16 LUFS et 11 LRA.
Il est important de garder à l'esprit que la commande loudnorm ne fonctionne qu'avec des fichiers audio au format mp3 et d'autres formats compatibles ffmpeg.
* Bitrate: Il permet d'attribuer la valeur dans les formats pris en charge.

Les commandes de conversion sont exécutées en arrière-plan via shell. Il émettra un son doux et constant qui représente le traitement, à la fin, un dialogue modal qui informe l'achèvement du processus est activé.
Les fichiers convertis sont enregistrés dans le dossier convertis, dans le répertoire sélectionné.

### Licences de tierces parties

[git/FFMpeg git summary](https://git.ffmpeg.org/ffmpeg.git)
