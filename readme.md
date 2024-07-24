# ffTools

Conjunto de herramientas del programa ffmpeg para el tratamiento de archivos multimedia.

[Gerardo Kessler](http://gera.ar/sonido/sobremi.php)  

Basado en el programa [ffmpeg](https://ffmpeg.org/)  

Descarga de los archivos binarios: <https://github.com/yt-dlp/FFmpeg-Builds/wiki/Latest>

Importante: Este módulo está basado en los binarios FF, por lo que es fundamental la descarga de estos archivos. El complemento ofrece descargarlos y guardarlos en el lugar correcto, aunque el usuario también puede hacerlo   copiando la carpeta bin con los archivos ffmpeg.exe y ffplay.exe en la raíz del complemento:

    %AppData%\nvda\addons\ffTools\globalPlugins\ffTools

## Comandos del complemento:

* Previsualizar el archivo de audio o video con el foco; Sin asignar
* Activar la capa de comandos; Sin asignar

### Comandos de previsualización

Una vez activada la previsualización, en la ventana de reproducción funcionan los siguientes comandos:

* Barra espaciadora; pausa y reanuda la reproducción
* Avance de página; Reproduce desde el inicio
* Flecha izquierda; retrocede en la línea de tiempo
* Flecha derecha; Avanza en la línea de tiempo
* Flecha arriba; aumenta el volúmen de reproducción
* Flecha abajo; disminuye el volúmen de reproducción
* Escape; cierra la ventana

### Capa de comandos

* f1; Abre este documento en el navegador por defecto
* f; Activa una ventana que permite modificar el volúmen, el formato, y el bitrate del archivo con el foco
* c; Activa una ventana que permite modificar la velocidad, cortar el inicio y el final del archivo con el foco
* l; Activa una ventana de conversión por lotes
* x; Extrae las pistas de audio del archivo de video con el foco

## Recorte

Al activar la capa de comandos y pulsar la letra c, se activa la ventana de velocidad y recorte.
Si la casilla de verificación "modificar velocidad del archivo" está marcada, solo se visualiza la lista de porcentajes a seleccionar.

De lo contrario hay disponibles 2 cuadros editables para seleccionar el comienzo y el final del corte. Si se quieren recortar los primeros 10 segundos del archivo, el cuadro debería editarse como 00:10. Es importante respetar el formato de 2 números para los minutos, y 2 para los segundos.
En el cuadro para el corte final, la etiqueta verbaliza el tiempo total del archivo, lo que también se verá reflejado en el valor del campo.
Para cortar los últimos 10 segundos del archivo, hay que editar el cuadro escribiendo el valor actual con los segundos restados. Si el archivo tiene una duración de 03:07, debería quedar 02:57.

### Conversión por lotes

Esta opción permite convertir todos los archivos soportados por FFMpeg existentes en un directorio.

Una vez activada la capa de comandos y pulsada la tecla l, se muestra una ventana de diálogo con las siguientes opciones:

* Ruta de carpeta: Aquí se muestra la ruta de la carpeta con los archivos.
* Examinar: Botón que abre el diálogo típico de Windows para buscar una carpeta con archivos a convertir.
* Formato a convertir: Lista de formatos de salida disponibles.
* Normalizar el volúmen de audio: Permite normalizar los audios a un nivel de sonoridad objetivo de -16 LUFS y 11 LRA.
Es importante tener en cuenta que el comando loudnorm solo funciona con archivos de audio en formato mp3 y otros formatos compatibles con ffmpeg.
* Bitrate: Permite asignar el valor en los formatos soportados.

Los comandos de conversión son ejecutados en segundo plano a través de shell. Un sonido suave y constante representa el procesamiento, al finalizar se activa un diálogo modal que notifica la finalización del proceso.
Los archivos convertidos se guardan en la carpeta convertidos, dentro del directorio seleccionado.

### Extracción de las pistas de audio de un video

Situados en el explorador de archivos de Windows sobre un archivo de video, y activada la capa de comandos con el gesto correspondiente, al pulsar la letra x se activa esta funcionalidad.
El proceso verifica cuantos streams de audio contiene el archivo, y en el caso de tener 1 o más, los extrae y los guarda en una carpeta que el módulo crea en la misma ruta del archivo y con el mismo nombre.
Los archivos se extraen en formato mp3 con el nombre stream y el número de pista. Al finalizar un diálogo modal notifica la finalización del proceso.

### Licencias de terceros

[git/FFMpeg git summary](https://git.ffmpeg.org/ffmpeg.git)
