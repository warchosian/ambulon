curl -LsSf https://code.kimi.com/install.sh  | bash
curl: (5) Could not resolve proxy: pfrie-std.proxy.e2.rie.gouv.fr

# Unset proxy variables for this session, then run the install
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
curl -LsSf https://code.kimi.com/install.sh | bash

curl --noproxy "*" -LsSf https://code.kimi.com/install.sh | bash

# See what proxy is configured
echo $http_proxy
echo $https_proxy

# If the proxy address is wrong, fix it:
export https_proxy="http://correct-proxy-address:port"

If you're on a corporate/government network (.gouv.fr suggests French government)
The proxy pfrie-std.proxy.e2.rie.gouv.fr might be:
Down or renamed - Contact your IT department
Only accessible from certain networks - Check if you're on the right network/VPN
Requiring authentication - You may need credentials
5. Alternative: Manual installation
If proxy issues persist, download the binary directly from a browser or another machine:
bash
Copy
# After downloading the appropriate binary for your system from:
# https://github.com/moonshot-ai/kimi-cli/releases
# Make it executable and move to your PATH:
chmod +x kimi
sudo mv kimi /usr/local/bin/
Which solution should you try?
Table
Situation	Recommended Solution
Just need this to work quickly	#1 or #2 (temporary bypass)
You need the proxy for other work	#3 (check/fix settings)
On government/corporate network	#4 (contact IT)
Nothing else works	#5 (manual install)
Try solution #1 first — it's the most likely to work immediately. Let me know if you need further help!
url --noproxy "*" -LsSf https://code.kimi.com/install.sh  | bash
curl: (6) Could not resolve host: code.kimi.com
Edit
Copy
Share
Now you're getting a different error: curl: (6) Could not resolve host: code.kimi.com. This means DNS resolution is failing entirely, which suggests your network configuration is more broadly affected.
Quick Solutions:
1. Check your internet connection first
bash
Copy
# Test if you can reach the internet at all
ping 8.8.8.8
curl -I https://www.google.com
2. Try using Google's DNS or check DNS settings
The host code.kimi.com might not resolve due to DNS issues. Try:
bash
Copy
# Check if it's a DNS problem
nslookup code.kimi.com
dig code.kimi.com

# If those fail, try with explicit DNS
curl --resolve code.kimi.com:443:108.156.91.81 -LsSf https://code.kimi.com/install.sh | bash
3. Alternative installation methods
Via GitHub (more reliable):
bash
Copy
# Download directly from GitHub releases
curl -LsSf https://github.com/moonshot-ai/kimi-cli/releases/latest/download/kimi-$(uname -s)-$(uname -m) -o kimi
chmod +x kimi
sudo mv kimi /usr/local/bin/
Or using pip (if you have Python):
bash
Copy
pip install kimi-cli
4. If you're behind a strict corporate/gov firewall
Your network might block:
External DNS resolution
Non-approved domains
Direct IP connections
Workarounds:
Use your phone's hotspot temporarily
Download the binary on another machine and transfer via USB
Contact your IT department to whitelist code.kimi.com or github.com
5. Verify the domain exists
Let me check if this is a real domain issue:
Search
kimi-cli installation code.kimi.com moonshot-ai/kimi-cli github releases
16 results
Good news — I found the official installation methods. The domain code.kimi.com is legitimate and the installation script is the recommended method . Since you can't resolve the host, here are working alternatives:
Best Alternative: Install via uv (Recommended)
Since you likely have Python, this bypasses the network issue entirely:
bash
Copy
# Install uv first (if you don't have it)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Then install kimi-cli directly
uv tool install --python 3.13 kimi-cli
Or with specific Python version:
bash
Copy
uv tool install --python 3.12 kimi-cli
Alternative: Download from GitHub Releases
Download the pre-built binary directly :
bash
Copy
# For Linux x86_64
curl -L -o kimi https://github.com/MoonshotAI/kimi-cli/releases/latest/download/kimi-linux-x86_64
chmod +x kimi
sudo mv kimi /usr/local/bin/

# For macOS (Apple Silicon)
curl -L -o kimi https://github.com/MoonshotAI/kimi-cli/releases/latest/download/kimi-darwin-arm64
chmod +x kimi
sudo mv kimi /usr/local/bin/
Alternative: Homebrew (if available)
bash
Copy
brew install kimi-cli
Alternative: pip (if uv doesn't work)
bash
Copy
pip install kimi-cli
Why You're Getting This Error
Your network appears to have both:
A broken proxy configuration (first error)
DNS resolution restrictions (second error)
The .gouv.fr domain suggests you're on a French government network with strict firewall rules. Try:
bash
Copy
# Check if you can reach GitHub at all
curl -I https://github.com


export http_proxy="http://pfrie-std.proxy.e2.rie.gouv.fr:8080"
export https_proxy="http://pfrie-std.proxy.e2.rie.gouv.fr:8080"
export HTTP_PROXY="$http_proxy"
export HTTPS_PROXY="$https_proxy"

# <<< conda init <<<
export http_proxy='http://pfrie-std.proxy.e2.rie.gouv.fr:8080/'
export https_proxy='https://pfrie-std.proxy.e2.rie.gouv.fr:8080/'
export PATH="$HOME/bin:$PATH"
export PATH="$HOME/tools/node-current/bin:$PATH"
export PATH="$HOME/.local/bin:$PATH"

# Proxy DIN/RIE
export http_proxy="http://pfrie-std.proxy.e2.rie.gouv.fr:3128"
export https_proxy="http://pfrie-std.proxy.e2.rie.gouv.fr:3128"
export no_proxy="localhost,127.0.0.1,.gouv.fr,.developpement-durable.gouv.fr,.rie.gouv.fr"