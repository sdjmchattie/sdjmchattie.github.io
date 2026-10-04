---
date: 2026-09-19
title: "Getting Started with Terraform: A Practical Guide to Infrastructure as Code"
description: |-
  Discover the power of Infrastructure as Code and how Terraform revolutionises cloud provisioning.
  Learn the core concepts, compare alternatives like Ansible and cloud-native templates, and build your first configuration.
slug: getting-started-with-terraform
image: /images/posts/2026/09-19-getting-started-with-terraform.png
tags:
  - Cloud Computing
  - Developer Tools
  - Software Architecture
---

{{< tldr >}}
[Terraform](https://www.terraform.io/) revolutionises cloud management by treating infrastructure as declarative, version-controlled code.
It ensures reproducible deployments across cloud providers through state tracking, execution planning, and provider ecosystems.

- **Declarative syntax:** Define desired cloud state in [HCL](https://github.com/hashicorp/hcl) without managing procedural deployment scripts.
- **Plan before apply:** Preview proposed infrastructure creations, changes, and destructions using `terraform plan`.
- **State management:** Store state files securely in remote backends with state locking to prevent deployment collisions.
- **Multi-cloud flexibility:** Manage AWS, GCP, Azure, and third-party SaaS tools through a unified workflow.
{{< /tldr >}}

Just like top terraformers in Minecraft reshape entire landscapes to build incredible worlds, mastering [Terraform](https://www.terraform.io/) in software engineering gives you complete control over your digital infrastructure.
Instead of manually clicking through cloud management consoles, you define your entire infrastructure estate in declarative code.

In this guide, I explore the virtues of Infrastructure as Code (IaC), examine how Terraform compares to other tools, and walk through the core syntax you need to get started.

## The Problem with ClickOps

When you first start building in the cloud, it is tempting to configure resources by hand.
You log into the AWS, Azure, or Google Cloud web console, click through menus, toggle checkboxes, and launch your servers.

This approach is colloquially known as "ClickOps", and it quickly breaks down as systems grow.
Manual setup creates several serious operational challenges:

- **Configuration drift**: Environments that are supposed to be identical slowly diverge because undocumented manual tweaks happen in production.
- **Human error**: Missing a single firewall rule or storage permission can cause outages or severe security vulnerabilities.
- **No audit trail**: It is nearly impossible to tell who changed a setting, when they changed it, or why.
- **Painful disaster recovery**: If an entire cloud region goes down, recreating dozens of interconnected services by hand takes hours or even days.

Infrastructure as Code solves every single one of these problems by treating your infrastructure with the exact same rigour as your application software.

## The Virtues of Infrastructure as Code

[Infrastructure as Code (IaC)](https://en.wikipedia.org/wiki/Infrastructure_as_code) is the practice of managing and provisioning computing resources through machine-readable definition files rather than physical hardware configuration or interactive web consoles.

### Reproducibility and consistency

With IaC, your infrastructure definitions serve as an unambiguous blueprint.
You can spin up an exact replica of your production environment for staging, testing, or local development within minutes.
This consistency eliminates the dreaded "it works in staging but fails in production" dilemma caused by mismatched cloud configurations.

### Version control and auditability

Because your infrastructure lives in text files, you store it directly in Git.
Every change goes through standard pull request reviews, automated linting, and security scans before deployment.
If something breaks, your Git history provides a complete audit trail showing exactly what changed, and you can roll back to a previous working commit instantly.

### Automated disaster recovery

When an outage strikes, you do not need to scramble through console pages trying to remember subnet IDs and routing tables.
You execute your deployment pipeline, and your entire cloud estate rebuilds itself automatically to the exact specifications stored in your repository.

## Navigating the IaC Landscape

The Infrastructure as Code ecosystem contains a variety of tools, and newcomers often wonder how they fit together.

### Provisioning versus configuration management

The most common point of confusion is the distinction between tools like **Terraform** and tools like [Ansible](https://www.ansible.com/), [Chef](https://www.chef.io/), or [Puppet](https://www.puppet.com/).

- **Infrastructure provisioning (Terraform)**: Specialised in creating foundational cloud resources from scratch.
  It creates virtual private clouds (VPCs), subnets, compute instances, object storage buckets, managed databases, and DNS records.
- **Configuration management (Ansible)**: Specialised in configuring operating systems and software *after* the servers exist.
  It installs packages, configures configuration files, manages Linux users, and starts background system services.

While Ansible can technically create cloud resources and Terraform can run shell scripts, teams achieve the best results by pairing them together: Terraform provisions the virtual machines, and Ansible configures the applications running on them.

### Cloud-native tools versus multi-provider agility

Major cloud vendors provide their own proprietary IaC solutions:

- **[AWS CloudFormation](https://aws.amazon.com/cloudformation/) & AWS CDK**: Purpose-built for Amazon Web Services.
- **Azure Resource Manager (ARM) & [Azure Bicep](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/)**: Tailored exclusively for Microsoft Azure.
- **Google Cloud Deployment Manager**: Designed solely for Google Cloud Platform.

These vendor-specific tools work well within their respective walled gardens, but they tie your workflows to a single cloud provider.
Learning Azure Bicep does not help you when you need to provision resources on AWS or manage DNS records on Cloudflare.

This is where Terraform shines.
Terraform uses a pluggable architecture powered by **providers**.
HashiCorp and the open-source community maintain thousands of providers that translate declarative configuration into native API calls for AWS, Azure, Google Cloud, Cloudflare, GitHub, Kubernetes, and Datadog.

It is worth clarifying what "portability" means here.
Terraform is not a "write once, run anywhere" abstraction layer.
Because AWS S3, Azure Blob Storage, and Google Cloud Storage have fundamentally different architectures, APIs, and access policies, you cannot write a generic storage block and deploy it unchanged across clouds.

Instead, Terraform gives you **workflow and skill portability**.
You write the exact same declarative HCL syntax, use the same CLI commands, and apply the same state management principles regardless of your target platform.
When you adopt a new cloud provider, you do not need to retrain your team on a completely new language or tooling ecosystem.

## Understanding Core Terraform Concepts

Terraform is built around a small set of straightforward concepts that work together predictably.

### Declarative syntax with HCL

Terraform uses [**HashiCorp Configuration Language (HCL)**](https://github.com/hashicorp/hcl).
HCL is a declarative language, which means you describe *what* you want your infrastructure to look like, not *how* to build it step by step.

Terraform inspects your desired state, queries your current infrastructure, calculates the differences, and builds an execution graph to apply the necessary changes in the correct order.

### Providers as plugins

Providers are plugins that tell Terraform how to interact with specific cloud platforms and SaaS APIs.
You declare the providers you need at the top of your configuration, and Terraform downloads the binaries automatically during initialisation.

### The state file

Terraform maintains a file named `terraform.tfstate` that acts as a database mapping your configuration to real-world resources.
When you define a storage bucket in HCL, the state file records its unique cloud ID, attributes, and metadata.

This state file allows Terraform to detect **drift**: if someone manually modifies a resource in the cloud console, Terraform detects the discrepancy on the next run and offers to restore the resource to your declared code configuration.

## Your First Terraform Configuration

Defining and managing cloud infrastructure with Terraform is straightforward once you understand the basic building blocks.

### Defining the infrastructure

You organise Terraform code in files ending with `.tf`.
A typical project includes a `main.tf` file where you declare your provider and desired resources.

Here is an example that configures the AWS provider and provisions a secure S3 bucket with versioning enabled:

```hcl
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-west-2"
}

variable "environment" {
  type        = string
  description = "Deployment environment name"
  default     = "production"
}

resource "aws_s3_bucket" "app_storage" {
  bucket = "my-unique-app-data-${var.environment}"

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket_versioning" "storage_versioning" {
  bucket = aws_s3_bucket.app_storage.id

  versioning_configuration {
    status = "Enabled"
  }
}

output "bucket_arn" {
  description = "The Amazon Resource Name of the storage bucket"
  value       = aws_s3_bucket.app_storage.arn
}
```

In this snippet, Terraform automatically recognises that `aws_s3_bucket_versioning` depends on `aws_s3_bucket.app_storage.id`.
It creates the bucket first, waits for AWS to confirm its creation, and then enables versioning without requiring any manual dependency flags.

If you wanted to provision equivalent object storage in Microsoft Azure instead, you would swap the `aws` provider for `azurerm` and declare an `azurerm_storage_container` resource.
While the specific resource arguments reflect each cloud's unique features, the structure, lifecycle commands, and variable mechanisms remain identical.

### The four-stage workflow

Managing infrastructure with Terraform follows four standard commands:

**1. Initialise your working directory (`terraform init`)**

Before you can run commands, you must initialise the directory.
This downloads the required provider plugins and configures the backend:

```bash
terraform init
```

**2. Preview planned changes (`terraform plan`)**

Next, generate an execution plan.
Terraform reads your code, checks the current state of your cloud environment, and outputs a detailed preview showing exactly what will be created (`+`), modified (`~`), or destroyed (`-`):

```bash
terraform plan
```

**3. Apply the changes (`terraform apply`)**

Once you review the plan and verify that everything looks correct, apply the changes:

```bash
terraform apply
```

Terraform prompts you for confirmation before executing any API calls against your cloud provider.

**4. Clean up resources (`terraform destroy`)**

When you no longer need an environment, you can tear down all managed infrastructure cleanly with a single command:

```bash
terraform destroy
```

## Essential Best Practices

As you adopt Terraform across your team, keeping a few critical principles in mind will save you from major headaches:

- **Store state remotely with locking**: Never store your production `terraform.tfstate` file on your local machine or commit it to Git.
  Use a remote backend such as an AWS S3 bucket paired with DynamoDB for state locking, or a dedicated platform like Terraform Cloud.
  This prevents team members from overwriting each other's concurrent runs.
- **Never commit secrets**: State files and variable files can contain sensitive tokens or database passwords in plain text.
  Always add `*.tfstate`, `*.tfstate.backup`, and `*.tfvars` to your `.gitignore` file.
- **Pin provider versions**: Always specify version constraints in your `required_providers` block.
  This prevents unexpected breaking changes when provider maintainers release new major versions.
- **Consider OpenTofu for open-source workflows**: Following HashiCorp's transition to the Business Source License (BSL) in 2023, the open-source community created [**OpenTofu**](https://opentofu.org/) under the Linux Foundation.
  OpenTofu serves as a drop-in, fully open-source alternative that supports the same HCL syntax and provider ecosystem.

## Wrapping Up

Adopting Infrastructure as Code transforms how you build and scale software.
By replacing manual console clicking with declarative Terraform blueprints, you gain rock-solid reproducibility, auditable change histories, and confidence in your deployments.

Whether you are managing a single virtual machine or orchestrating multi-cloud architectures across AWS, Azure, and Cloudflare, Terraform provides a unified toolchain that scales with your ambitions.

To explore further, I recommend installing the Terraform CLI, trying out the local Docker provider on your machine, and experimenting with modular configurations.
