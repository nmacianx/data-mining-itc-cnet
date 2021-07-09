/*
 Navicat Premium Data Transfer

 Source Server         : Alex2
 Source Server Type    : MySQL
 Source Server Version : 50726
 Source Host           : localhost:3306
 Source Schema         : data_mining

 Target Server Type    : MySQL
 Target Server Version : 50726
 File Encoding         : 65001

 Date: 02/07/2021 16:21:11
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for article
-- ----------------------------
DROP TABLE IF EXISTS `article`;
CREATE TABLE `article`  (
  `id_article` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `date` datetime(0) NOT NULL,
  `url` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  PRIMARY KEY (`id_article`) USING BTREE,
  UNIQUE INDEX `title`(`title`, `date`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = latin1 COLLATE = latin1_swedish_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for author
-- ----------------------------
DROP TABLE IF EXISTS `author`;
CREATE TABLE `author`  (
  `id_author` int(11) NOT NULL AUTO_INCREMENT,
  `nick_name` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `name` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `location` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `occupation` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `url` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `member_since` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  PRIMARY KEY (`id_author`) USING BTREE,
  UNIQUE INDEX `nick_name`(`nick_name`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = latin1 COLLATE = latin1_swedish_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for hashtag
-- ----------------------------
DROP TABLE IF EXISTS `hashtag`;
CREATE TABLE `hashtag`  (
  `id_hashtag` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `url` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `is_topic` bit(1) DEFAULT NULL,
  PRIMARY KEY (`id_hashtag`) USING BTREE,
  UNIQUE INDEX `name`(`name`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = latin1 COLLATE = latin1_swedish_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for article_author
-- ----------------------------
DROP TABLE IF EXISTS `article_author`;
CREATE TABLE `article_author`  (
  `id_article_author` int(11) NOT NULL AUTO_INCREMENT,
  `id_author` int(11) NOT NULL,
  `id_article` int(11) NOT NULL,
  PRIMARY KEY (`id_article_author`) USING BTREE,
  UNIQUE INDEX `id_author`(`id_author`, `id_article`) USING BTREE,
  INDEX `id_article`(`id_article`) USING BTREE,
  CONSTRAINT `article_author_ibfk_1` FOREIGN KEY (`id_author`) REFERENCES `author` (`id_author`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `article_author_ibfk_2` FOREIGN KEY (`id_article`) REFERENCES `article` (`id_article`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = latin1 COLLATE = latin1_swedish_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for article_hashtag
-- ----------------------------
DROP TABLE IF EXISTS `article_hashtag`;
CREATE TABLE `article_hashtag`  (
  `id_article_hashtag` int(11) NOT NULL AUTO_INCREMENT,
  `id_article` int(11) NOT NULL,
  `id_hashtag` int(11) NOT NULL,
  PRIMARY KEY (`id_article_hashtag`) USING BTREE,
  UNIQUE INDEX `id_article`(`id_article`, `id_hashtag`) USING BTREE,
  INDEX `id_hashtag`(`id_hashtag`) USING BTREE,
  CONSTRAINT `article_hashtag_ibfk_1` FOREIGN KEY (`id_article`) REFERENCES `article` (`id_article`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `article_hashtag_ibfk_2` FOREIGN KEY (`id_hashtag`) REFERENCES `hashtag` (`id_hashtag`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = latin1 COLLATE = latin1_swedish_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
