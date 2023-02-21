# ffTools

Conjunto de herramientas del programa ffmpeg para la previsualización de audio y video, Normalización de volúmen y conversiones de formato.

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
* Avance de página; Reproduce desde el inicio.
* Flecha izquierda; retrocede en la línea de tiempo.
* Flecha derecha; Avanza en la línea de tiempo.
* Flecha arriba; aumenta el volúmen de reproducción.
* Flecha abajo; disminuye el volúmen de reproducción.
* Escape; cierra la ventana

### Capa de comandos

* f1; Abre este documento en el navegador por defecto.
* f; Activa una ventana que permite modificar el volúmen, el formato, y el bitrate del archivo con el foco 
* c; Activa una ventana que permite modificar la velocidad, cortar el inicio y el final del archivo con el foco 
* l; Activa una ventana de conversión en lote

Conversión por lotes

Esta opción permite convertir todos los archivos soportados por FFMpeg existentes en un directorio.

Una vez activada la capa de comandos y pulsada la tecla l, se muestra una ventana de diálogo con las siguientes opciones:

* Ruta de carpeta: Aquí se muestra la ruta de la carpeta con los archivos.
* Examinar: Botón que abre el diálogo típico de Windows para buscar una carpeta con archivos a convertir.
* Formato a convertir: Lista de formatos de salida disponibles.
* Normalizar el volúmen de audio: Permite normalizar los audios a un nivel de sonoridad objetivo de -16 LUFS y 11 LRA.
Es importante tener en cuenta que el comando loudnorm solo funciona con archivos de audio en formato mp3 y otros formatos compatibles con ffmpeg.
* Bitrate: Permite asignar el valor en los formatos soportados.

Todos estos comandos son ejecutados en segundo plano a través de shell. Un sonido suave y constante representa el procesamiento, que culmina con un sonido breve al finalizar.
