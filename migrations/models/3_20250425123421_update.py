from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `du` DROP INDEX `num1`;
        ALTER TABLE `du` DROP INDEX `num3`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `du` ADD UNIQUE INDEX `num3` (`num3`);
        ALTER TABLE `du` ADD UNIQUE INDEX `num1` (`num1`);"""


