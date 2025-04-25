from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `TXT` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `book_name` VARCHAR(200) NOT NULL COMMENT '小说名',
    `book_title` LONGTEXT NOT NULL COMMENT '章节标题',
    `book_txt` VARCHAR(200) NOT NULL COMMENT '章节内容',
    `book_nums` INT COMMENT '章节数'
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
