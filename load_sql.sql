CREATE TABLE "ccu_gen_beta_orgstance_orgstances" (
    "id" integer NOT NULL PRIMARY KEY,
    "repcontributionreport_id" integer NOT NULL REFERENCES "ccu_gen_beta_repcontributionreport" ("id"),
    "orgstance_id" integer NOT NULL REFERENCES "ccu_gen_beta_orgstance" ("id"),
    UNIQUE ("repcontributionreport_id", "orgstance_id")
);
