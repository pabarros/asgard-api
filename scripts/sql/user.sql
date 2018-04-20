\c asgard;

insert into account (name, namespace, owner) values ('Asgard/DEV', 'asgard-dev', 'asgard-dev');
insert into account (name, namespace, owner) values ('Asgard/INFRA', 'asgard-infra', 'asgard-infra');

insert into "user" (tx_name, tx_email, tx_authkey, bl_system) values ('Rafael Amorim', 'rafael@admatic.com.br', 'cccccchcdhjrtrgbtndbedljrectjhv', false);
INSERT INTO "user" (tx_name, tx_email, tx_authkey, bl_system) VALUES ('Dalton Barreto', 'daltonmatos@gmail.com', '15ce068d5d2942b18a7f8ae76933f53', false);


INSERT INTO user_has_account (account_id, user_id) VALUES (
  (SELECT id from account where name = 'Asgard/DEV'),
  (SELECT id from "user" where tx_email='daltonmatos@gmail.com')
);

INSERT INTO user_has_account (account_id, user_id) VALUES (
  (SELECT id from account where name = 'Asgard/INFRA'),
  (SELECT id from "user" where tx_email='daltonmatos@gmail.com')
);

INSERT INTO user_has_account (account_id, user_id) VALUES (
  (SELECT id from account where name = 'Asgard/DEV'),
  (SELECT id from "user" where tx_email='rafael@admatic.com.br')
);

INSERT INTO user_has_account (account_id, user_id) VALUES (
  (SELECT id from account where name = 'Asgard/INFRA'),
  (SELECT id from "user" where tx_email='rafael@admatic.com.br')
);
