-- init.sql
CREATE DATABASE IF NOT EXISTS GridTradingView;
GRANT ALL PRIVILEGES ON GridTradingView.* TO 'LeRequeteur'@'%';
FLUSH PRIVILEGES;