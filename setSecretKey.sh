# Randomly generate a secret key. ONLY USE THIS FOR DEVELOPMENT!
export SECRET_KEY=`date +%s | sha256sum | base64 | head -c 32 ; echo`