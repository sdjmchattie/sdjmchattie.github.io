---
date: 2025-05-03
title: "Setting up a cheap home server using Raspberry Pi"
description: |-
  Having a home server may seem like an unnecessary maintenance burden for many, but it opens up so many possibilities.
  Mine is used to provide ad-blocking to my whole house using Pi-Hole, to run home automation tasks with Home Assistant, and to run software that should always be available using Docker.
slug: setup-a-raspberry-pi-home-server
image: /images/posts/2025-05-03-raspberry-pi-server.jpg
tags:
  - Raspberry Pi
  - Home Assistant
  - Pi-Hole
  - Docker
  - Portainer
  - Self Hosting
---

A Raspberry Pi home server offers a low-cost, high-flexibility solution for everything from ad-blocking to home automation.
Here's how you can set one up with ease.

If you like this post and you'd like to know more about uses for Raspberry Pis, check out the page for the [Raspberry Pi]({{< ref "/tags/raspberry-pi" >}}) tag.

Running a server at home may seem like unnecessary work to some, but it opens up a world of possibilities.
From network-wide ad-blocking, to home automation, to self-hosting applications — a Raspberry Pi can handle it all.

In this post, we'll walk through the basics of setting up a home server with a Raspberry Pi.
We'll cover hardware recommendations, installation of the operating system, network configuration, and installing useful services like Pi-Hole, Home Assistant, and Docker.

By the end, you’ll have a flexible and inexpensive server running at home with minimal fuss.

Let’s get started.

## Choosing Your Raspberry Pi and Accessories

You don't need the latest hardware for a home server — a Raspberry Pi 3B or newer is a good starting point.
We won't be running the graphical interface, so the requirements are quite low.

The 3B is a particularly attractive choice because it uses much less power than newer models, making it cheaper to run and easier to power reliably.

For storage, while a MicroSD card works, they can become unreliable over time with heavy use.
Instead, consider a USB 3.0 thumb drive or a small SSD for better speed and durability.

A good case keeps the Raspberry Pi safe from knocks and bumps.
I recommend the FLIRC cases because they double as a massive heatsink, keeping your Pi cool without needing a fan and helping prevent performance throttling.

Finally, make sure your power supply matches the needs of your Pi model.
The official power supply is usually the safest option and is not too expensive.
The 3B’s lower power requirements means you can use almost any power supply and still get a good result.

## Installing the Operating System

There are lots of operating systems available for the Raspberry Pi, but the easiest option is to use the official Raspberry Pi OS.
It’s lightweight, well-supported, and perfect for a home server setup.

The simplest way to install it is with the Raspberry Pi Imager tool.
You can download the Imager from the official site: [https://www.raspberrypi.com/software/](https://www.raspberrypi.com/software/)

Once you have it installed:

- Insert your MicroSD card, USB drive, or SSD into your computer. (***Note:*** it will be wiped clean!)
- Open Raspberry Pi Imager.
- Select "Raspberry Pi OS (Lite)" under the Operating System section. (We don't need the desktop environment)
- Choose your storage device.
- When you move on to writing, you will be offered to pre-configure settings like enabling SSH, setting a default username and password and choosing a host name.
  You should do this so you don't need to hook up a monitor.
  Take note of the options you selected as you'll need these soon.
- Start the process off and wait for it to finish.

After a few minutes, your storage device will be ready to boot your Raspberry Pi.

## First Boot and Basic Configuration

Once you’ve written the OS to your storage device and configured your network settings, it’s time to boot up your Raspberry Pi.

Insert the MicroSD card, USB drive, or SSD into the Pi and power it on.

If you configured SSH earlier, you can connect to your Pi using an SSH client (like PuTTY or Terminal) by entering its host name.
For example, on macOS Terminal, you would use `ssh <username>@<hostname>.local` to connect.

On the first boot, you may want to:

- Update the system with the latest patches:

      sudo apt update && sudo apt upgrade -y

- Change the default password for added security:

      passwd

- Set the system locale and time zone.
  Use the menu to adjust your settings as necessary:

      sudo raspi-config

- Set a static IP address.
  Servers should use static IP addresses:

  - Open the network manager tool:

        sudo nmtui

  - Choose to "Edit a connection".
  - Select the network connection you're using (preferably wired ethernet for a server).
  - Add the following values to fields, ensuring they're compatible with your network:
    - IPv4 Configuration: `Manual`
    - Addresses: `192.168.1.250/24`
    - Gateway: `192.168.1.1`
    - DNS Servers: `8.8.8.8` and `8.8.4.4`
  - Save and exit the application.
  - Reboot with `sudo reboot`.

This is the bit where you hope all your settings were good.
If you find that you can't connect to the server on its new IP address after a reboot, there's a good chance the network connection settings were bad.
In this case, the easiest way to continue is to hook the Raspberry Pi up to a monitor, keyboard and mouse and check them over again before trying another reboot.

Once that's done, your Raspberry Pi is ready to go.

## Installing and Configuring the Services I Use

Now that your Raspberry Pi is up and running, let’s install and configure the key services that I use on my home server.

### Pi-Hole

Pi-Hole blocks ads for every device on your network and can handle both DNS (domain name resolution) and DHCP (dynamic IP address assignment).
The DNS is how it blocks ads, by making known ad servers appear to no longer exist on the internet.

I prefer to run pi-hole directly on the machine rather than in a container as I use it for both DNS and DHCP.
When it stops working the whole network stops with it so I like to remove all complicating factors.

Installation is as simple as:

    sudo curl -sSL https://install.pi-hole.net | bash

Follow the instructions carefully and choose your ad-blocking needs.
Once installed you can use the admin interface to change settings by going to [http://192.168.1.250/admin](http://192.168.1.250/admin) or whatever IP you set earlier.

Once pi-hole is running, you need to go to your regular network router and tell it to use a custom DNS server, pointing it at `192.168.1.250`.
When devices next disconnect and reconnect to the network, they should start routing their DNS through pi-hole and receive ad-blocking by default.

### Docker and Portainer

Installing Docker is about as simple as it was to install pi-hole:

    curl -sSL https://get.docker.com | sh

Normally you need to use `sudo` for every Docker command, but you can grant Docker access to the `pi` user by adding it to the `docker` group:

    sudo usermod -aG docker pi

Reboot the Raspberry Pi and you should find that the command `docker ps` now shows an empty list of running containers.

Portainer lets you easily setup and run stacks of containers that work to provide applications on the network.
Portainer is actually itself a container that runs in Docker, so you install it by creating a volume for it and then running the container with restart enabled:

    docker volume create portainer_data
    docker run -d -p 9000:9000 --name portainer --restart always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce

Once it's running, you can access the web admin page at [http://192.168.1.250:9000](http://192.168.1.250:9000) or whatever IP address your server is running at.

### Home Assistant as a Docker Stack

Now that we have Portainer, we can use the admin interface to set up an instance of Home Assistant:

- Click the "Live Connect" button for the local environment.
- Click "Stacks" in the left hand menu.
- Click "Add Stack" and name it "homeassistant", choosing to use the web editor.
- Put the following in as the docker compose contents:

      services:
        homeassistant:
          image: "homeassistant/home-assistant:stable"
          restart: always
          privileged: true
          network_mode: host
          volumes:
            - /var/lib/homeassistant/config:/config
            - /etc/localtime:/etc/localtime:ro

- Click "Deploy the Stack" and wait until it is up and running.
  This can take a while!

Once Home Assistant is up and running, you can access it at [http://192.168.1.250:8123](http://192.168.1.250:8123) or whatever IP address you set up for the server.

Config for Home Assistant will be stored locally on the Raspberry Pi OS system under `/var/lib/homeassistant/config` so you can use that when you want to add custom components or to backup your settings if needed.

## Other Uses

Your Raspberry Pi home server can do much more than just Pi-Hole and Home Assistant.
Here are a few additional ideas:

- **Media Server**: Host a media server with Plex or Jellyfin to stream movies and music to all your devices.
- **Cloud Storage**: Set up Nextcloud or ownCloud for personal cloud storage and file sharing.
- **Git Server**: Host a private Git server with GitLab or Gitea for version control and collaboration.
- **VPN**: Set up a VPN (e.g., OpenVPN or WireGuard) to securely access your home network remotely.
- **Web Server**: Run a web server (e.g., Nginx or Apache) to host personal websites or blogs.

The Raspberry Pi’s versatility means you can customize it to fit your needs and explore countless other use cases.
Just keep in mind that some of these services require a bit more power than the 3B may be able to offer, so you might want to consider using a more powerful model.

## Wrapping Up

By now, you have a fully functioning Raspberry Pi home server with ad-blocking, automation, and the flexibility to run Docker containers for all sorts of applications.

Setting up a Raspberry Pi as a home server is a low-cost, flexible way to add a variety of services to your home network.
Whether you use it for ad-blocking, home automation, or as a media server, the possibilities are endless.

While this guide covers the basics at a very high level, maybe there could be more detail about a specific tool used here.
If you’d like to dive deeper into any of these topics, feel free to [get in touch]({{< ref "/#contact" >}} "Contact Me")!

Happy tinkering!
