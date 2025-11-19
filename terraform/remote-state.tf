module "remote_state" {
  source              = "./modules/remote-state"
  state_bucket_name   = "sample-state-bucket"
  dynamodb_table_name = "sample-state-locks-table"
}