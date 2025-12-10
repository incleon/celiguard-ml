# Deploy CeliGuard ML to Google Cloud (Free Tier)

This guide covers deploying the CeliGuard ML application to a Google Compute Engine VM (Free Tier) with HTTPS support.

## Prerequisites
- Google Cloud SDK (`gcloud`) installed and authenticated
- A Google Cloud Project
- A domain name (required for HTTPS)

## 1. Create VM (Free Tier)

Run the following command to create an `e2-micro` instance (Free Tier eligible) in `us-central1-a`:

```bash
gcloud compute instances create celiguard-ml-vm \
  --zone=us-central1-a \
  --machine-type=e2-micro \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=20GB \
  --tags=celiguard-ml
```

## 2. Configure Firewall

Allow HTTP (80), HTTPS (443), and application ports:

```bash
gcloud compute firewall-rules create celiguard-allow-web \
  --action ALLOW \
  --rules "tcp:80,tcp:443,tcp:8000,tcp:8501" \
  --source-ranges "0.0.0.0/0" \
  --description "Allow web traffic"
```

## 3. Configure DNS

Point your domain to the VM's external IP address.
1. Get the IP:
   ```bash
   gcloud compute instances describe celiguard-ml-vm --zone=us-central1-a --format="value(networkInterfaces[0].accessConfigs[0].natIP)"
   ```
2. Create **A Records** in your DNS provider:
   - `yourdomain.com` -> `[VM_IP]`
   - `api.yourdomain.com` -> `[VM_IP]`

## 4. Deploy Application

SSH into the VM and set up the application:

```bash
gcloud compute ssh celiguard-ml-vm --zone=us-central1-a
```

Inside the VM, run:

```bash
# 1. Install Docker & Git
sudo apt-get update && sudo apt-get install -y docker.io docker-compose git

# 2. Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# 3. Clone Repository
git clone https://github.com/ayush-yadavv/celiguard-ml.git
cd celiguard-ml
git checkout ft-add-ay

# 4. Upload Models (Run this from your LOCAL machine, not VM)
# gcloud compute scp models/*.pkl celiguard-ml-vm:~/celiguard-ml/models/ --zone=us-central1-a

# 5. Start Services
docker-compose up -d --build
```

## 5. Setup HTTPS (Caddy)

We use Caddy for automatic HTTPS. Inside the VM:

1. **Install Caddy**:
   ```bash
   sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
   curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
   curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
   sudo apt update
   sudo apt install caddy
   ```

2. **Configure Caddy**:
   Create `/etc/caddy/Caddyfile`:
   ```bash
   sudo nano /etc/caddy/Caddyfile
   ```
   
   Add your domains:
   ```
   yourdomain.com {
       reverse_proxy localhost:8501
   }

   api.yourdomain.com {
       reverse_proxy localhost:8000
   }
   ```

3. **Reload Caddy**:
   ```bash
   sudo systemctl reload caddy
   ```

## Maintenance

- **Update Code**:
  ```bash
  git pull
  docker-compose up -d --build
  ```

- **View Logs**:
  ```bash
  docker-compose logs -f
  ```

- **Restart Services**:
  ```bash
  docker-compose restart
  ```


