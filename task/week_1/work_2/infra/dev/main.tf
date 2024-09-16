module "cvm" {
  source = "../module/cvm"
  secret_id = var.secret_id
  secret_key = var.secret_key
  password = var.password
  region = var.region
}

module "k3s" {
  source = "../module/k3s"
  public_ip = module.cvm.public_ip
  private_ip = module.cvm.private_ip
}

module "argocd" {
  source     = "../module/helm"
  kube_config = local_sensitive_file.kubeconfig.filename
  name = "argocd"
  namespace = "argocd"
  chart = "argo-cd"
  repository = "https://argoproj.github.io/argo-helm"
}

module "crossplane" {
  source     = "../module/helm"
  kube_config = local_sensitive_file.kubeconfig.filename
  name = "crossplane"
  namespace = "crossplane-system"
  chart = "crossplane"
  repository = "https://charts.crossplane.io/stable"
}

resource "local_sensitive_file" "kubeconfig" {
  content  = module.k3s.kube_config
  filename = "${path.module}/config.yaml"
}