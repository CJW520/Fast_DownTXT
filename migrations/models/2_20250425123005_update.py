from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `TXT` MODIFY COLUMN `txt` LONGTEXT NOT NULL COMMENT '章节内容';
        CREATE TABLE IF NOT EXISTS `du` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `num1` INT NOT NULL UNIQUE,
    `num2` INT NOT NULL,
    `num3` INT NOT NULL UNIQUE,
    `type` VARCHAR(100) NOT NULL
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `user` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(50) NOT NULL UNIQUE,
    `password` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) NOT NULL UNIQUE
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `TXT` MODIFY COLUMN `txt` VARCHAR(200) NOT NULL COMMENT '章节内容';
        DROP TABLE IF EXISTS `user`;
        DROP TABLE IF EXISTS `du`;"""



