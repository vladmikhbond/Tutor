cd c:\git\dock\durometer
docker stop duro_img
docker rm duro_img
docker image rm duro_img
docker build -t duro_img .
docker save -o "G:\My Drive\tar\duro.tar" duro_img