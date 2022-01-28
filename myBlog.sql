/*
encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/27
@gituhb: sanxiadaba/pythonBlog
*/


SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for article
-- ----------------------------
DROP TABLE IF EXISTS `article`;
CREATE TABLE `article`
(
    `articleid`   int(11)                                                       NOT NULL AUTO_INCREMENT COMMENT 'Article id',
    `userid`      int(11)                                                       NOT NULL COMMENT 'Author\'s id',
    `type`        tinyint(4)                                                    NOT NULL DEFAULT 1 COMMENT 'Types of columns 1, 2, 3, 4... Corresponds to the name of the column set in constant',
    `headline`    varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Title of the article',
    `content`     mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT 'Content of the article',
    `thumbnail`   varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT 'Address of article thumbnails (default in /static/img/thumb directory)',
    `credit`      int(10)                                                       NOT NULL DEFAULT 0 COMMENT 'Points needed to view articles',
    `readcount`   int(10)                                                       NOT NULL DEFAULT 0 COMMENT 'Reads',
    `replycount`  int(10)                                                       NOT NULL DEFAULT 0 COMMENT 'The number of replies to comments on articles',
    `recommended` tinyint(4)                                                    NULL     DEFAULT 0 COMMENT 'Whether the article is a recommended article or not is 1 if yes or 0 if no',
    `hide`        tinyint(4)                                                    NULL     DEFAULT 0 COMMENT 'Whether the article is hidden or not, if hidden is 1, it will not be displayed (the article is still in the database)',
    `drafted`     tinyint(4)                                                    NULL     DEFAULT 0 COMMENT 'Determine if the article is a draft, if so 1',
    `checked`     tinyint(4)                                                    NULL     DEFAULT 1 COMMENT 'Determine whether the article has been audited, not audited for 1, to the administrator to review',
    `createtime`  datetime(0)                                                   NULL     DEFAULT NULL COMMENT 'Creation time of the article',
    `updatetime`  datetime(0)                                                   NULL     DEFAULT NULL COMMENT 'Update time of the article',
    `delete`      tinyint(4)                                                    NULL     DEFAULT 0 COMMENT 'Determine if the author has removed this article',
    PRIMARY KEY (`articleid`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 1
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for articleLog
-- ----------------------------
DROP TABLE IF EXISTS `articleLog`;
CREATE TABLE `articleLog`
(
    `articleLogId` int(11)                                                       NOT NULL AUTO_INCREMENT COMMENT 'This table is used to record the posting, draft and revision records of articles\n',
    `userid`       int(11)                                                       NULL DEFAULT NULL COMMENT 'User id for this operation',
    `articleid`    int(11)                                                       NULL DEFAULT NULL COMMENT 'The id number of the draft or article',
    `type`         varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'Classification of article placement',
    `ipaddr`       varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'The ip address for this operation',
    `info`         varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'Note on this operation',
    `createtime`   datetime(0)                                                   NULL DEFAULT NULL COMMENT 'Operation time of this operation',
    PRIMARY KEY (`articleLogId`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 1
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for comment
-- ----------------------------
DROP TABLE IF EXISTS `comment`;
CREATE TABLE `comment`
(
    `commentid`   int(11)                                                       NOT NULL AUTO_INCREMENT COMMENT 'The id serial number of the comment',
    `userid`      int(11)                                                       NULL DEFAULT NULL COMMENT 'Comments made by the user of that id',
    `articleid`   int(11)                                                       NULL DEFAULT NULL COMMENT 'Which article to comment on',
    `content`     text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci         NULL COMMENT 'What is the content of the comments',
    `ipaddr`      varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'The ip address of the comment',
    `replyid`     int(11)                                                       NULL DEFAULT 0 COMMENT 'Determine whether the comment is the original comment or a reply comment, if the original comment the value is 0, otherwise the value is the commentid of the reply comment',
    `agreecount`  int(255)                                                      NULL DEFAULT 0 COMMENT 'Number of Likes',
    `opposecount` int(255)                                                      NULL DEFAULT 0 COMMENT 'Number of objections',
    `hide`        tinyint(4)                                                    NULL DEFAULT 0 COMMENT 'Whether to hide, 0 is not hidden, 1 is hidden\n',
    `createtime`  datetime(0)                                                   NULL DEFAULT NULL COMMENT 'Comment creation time',
    `info`        varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'Additional instructions for adding comments',
    PRIMARY KEY (`commentid`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 1
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for credit
-- ----------------------------
DROP TABLE IF EXISTS `credit`;
CREATE TABLE `credit`
(
    `creditid`   int(10)                                                       NOT NULL AUTO_INCREMENT COMMENT 'This table is used to record the change in points',
    `userid`     int(10)                                                       NOT NULL COMMENT 'User id',
    `category`   varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'Categories of point changes, e.g. \"login plus points\", \"registration plus points\"',
    `target`     int(255)                                                      NULL DEFAULT NULL COMMENT 'Add points to which article\n',
    `createtime` datetime(0)                                                   NULL DEFAULT NULL COMMENT 'Time of operation',
    `ipaddr`     varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'Address of the operation',
    `info`       varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'Explanation of point changes',
    `credit`     int(255)                                                      NULL DEFAULT NULL COMMENT 'How many change points (can be negative)',
    PRIMARY KEY (`creditid`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 1
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for favorite
-- ----------------------------
DROP TABLE IF EXISTS `favorite`;
CREATE TABLE `favorite`
(
    `favoriteid` int(11)      NOT NULL AUTO_INCREMENT COMMENT 'This table is used to record information about users\' favorite or unfavorite articles',
    `articleid`  int(11)      NULL DEFAULT NULL COMMENT 'Favorite or unfavorite the id of the article',
    `userid`     int(11)      NULL DEFAULT NULL COMMENT 'Which user made or unmade the favorites',
    `canceled`   tinyint(255) NULL DEFAULT 0 COMMENT 'Whether the collection has been canceled (after canceling the collection, it does not directly delete the data, but back to make a mark)',
    `createtime` datetime(0)  NULL DEFAULT NULL COMMENT 'Time of collection',
    PRIMARY KEY (`favoriteid`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 1
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for log
-- ----------------------------
DROP TABLE IF EXISTS `log`;
CREATE TABLE `log`
(
    `logid`      int(11)                                                       NOT NULL AUTO_INCREMENT COMMENT 'This table is used to record the very many operations done by the user',
    `userid`     int(11)                                                       NOT NULL COMMENT 'The userid of the operator',
    `category`   varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT 'Operation Category',
    `target`     int(11)                                                       NULL DEFAULT 0 COMMENT 'Operation target (such as commenting or posting articles is the id of the article), others such as daily login is 0',
    `credit`     int(11)                                                       NULL DEFAULT NULL COMMENT 'Point changes resulting from this operation',
    `createtime` datetime(0)                                                   NULL DEFAULT NULL COMMENT 'Operation time\n',
    `ipaddr`     varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'Operation Address',
    `info`       varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'Additional description information',
    PRIMARY KEY (`logid`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 1
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for upload
-- ----------------------------
DROP TABLE IF EXISTS `upload`;
CREATE TABLE `upload`
(
    `uploadid`   int(11)                                                       NOT NULL AUTO_INCREMENT COMMENT 'This table is used to record the record of uploaded images',
    `userid`     int(11)                                                       NULL DEFAULT NULL COMMENT 'Userid of the uploaded image',
    `imgname`    varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'Location of uploaded images',
    `ipaddr`     varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'The ip address of the operation',
    `info`       varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'Notes on this operation',
    `createtime` datetime(0)                                                   NULL DEFAULT NULL COMMENT 'Creation time of this operation',
    PRIMARY KEY (`uploadid`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 1
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`
(
    `userid`      int(11)                                                       NOT NULL AUTO_INCREMENT COMMENT 'This table is used to record information about the user',
    `username`    varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NOT NULL COMMENT 'User Name',
    `password`    varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NOT NULL COMMENT 'Login password (encrypted with md5)',
    `nickname`    varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT NULL COMMENT 'Nickname',
    `avatar`      varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT 'Avatar Address',
    `qq`          varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT NULL COMMENT 'Account\'s qq number',
    `role`        varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NOT NULL DEFAULT 'user' COMMENT 'The roles of users are divided into \"Administrator\", \"User\" and \"Editor\". Users need to submit articles to be reviewed by the administrator before they can be published, and editors can publish articles directly without review.',
    `credit`      int(11)                                                       NOT NULL DEFAULT 50 COMMENT 'Total user points',
    `createtime`  datetime(0)                                                   NULL     DEFAULT NULL COMMENT 'Time of user creation',
    `apply`       int(1)                                                        NULL     DEFAULT 0 COMMENT 'Whether to apply to become an editor',
    `agreeEditor` tinyint(1)                                                    NULL     DEFAULT 0 COMMENT 'Does the administrator agree to become an editor',
    `fobidLogin`  tinyint(1)                                                    NULL     DEFAULT 0 COMMENT 'Does the administrator disable this user from logging in',
    PRIMARY KEY (`userid`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 1
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci
  ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
