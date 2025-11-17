module "remote_state" {
  source              = "./modules/remote-state"
  state_bucket_name   = "terraform-state-bucket-team5-opensource"
  dynamodb_table_name = "terraform-locks"
}