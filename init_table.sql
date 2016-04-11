drop table if exists rasp_sysset;
create table rasp_sysset (
  id integer primary key autoincrement,
  name text not null,
  value text not null
);