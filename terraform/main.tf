terraform {
	backend "gcs" {
		bucket = "rl-route-optimization-tf-state"
		prefix = "terraform/state"
	}
	required_providers {
		google = {
			source = "hashicorp/google"
			version = "~> 5.0"
		}
	}
}

provider "google" {
	project = "rl-route-optimization"
	region = "australia-southeast1"
}

# 1. Secret Manager (Holds the API Token)
resource "google_secret_manager_secret" "api_token" {
	secret_id = "api-auth-token"
	replication {
		auto {}
	}
}

resource "google_secret_manager_secret_version "api_token_version" {
	secret = google_secret_manager_secret.api_token.id
	secret_data = "secret-production-token"
}

# 2. Cloud Run Service
resource "google_cloud_run_v2_service" "default" {
	name = "rl-route-optimization"
	location = "australia-southeast1"
	
	template {
		containers {
			# Points to the Docker image GitHub Actions will build
			image = "australia-southeast1-docker.pkg.dev/rl-route-optimization/rl-route-optimization/routing-engine:latest"
			
			env {
				name = "API_AUTH_TOKEN"
				value_source {
					secret_key_ref {
						secret = google_secret_manager_secret.api_token.secret_id
						version = "latest"
					}
				}
			}
		}
	}
}

# 3. Use FastAPI to handle the actual security check
resource "google_cloud_run_service_iam_member" "public" {
	service = google_cloud_run_v2_service.default.name
	location = google_cloud_run_v2_service.default.location
	role = "roles/run.invoker"
	member = "allUsers"
}