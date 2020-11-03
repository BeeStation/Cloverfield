-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               10.5.6-MariaDB-1:10.5.6+maria~focal - mariadb.org binary distribution
-- Server OS:                    debian-linux-gnu
-- HeidiSQL Version:             11.0.0.5919
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;

-- Dumping structure for table goonhub.bans
CREATE TABLE IF NOT EXISTS `bans` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ckey` tinytext DEFAULT NULL,
  `ip` bigint(20) DEFAULT NULL,
  `cid` bigint(20) DEFAULT NULL,
  `akey` tinytext DEFAULT NULL,
  `oakey` tinytext DEFAULT NULL,
  `reason` text DEFAULT NULL,
  `timestamp` bigint(20) DEFAULT NULL COMMENT 'BYOND Era timestamp...',
  `previous` int(11) DEFAULT NULL COMMENT 'Previous Ban',
  `chain` int(11) DEFAULT NULL COMMENT 'ban evasion chain len',
  `removed` tinyint(4) DEFAULT 0 COMMENT 'Removed in some way ',
  PRIMARY KEY (`id`),
  KEY `ip` (`ip`),
  KEY `cid` (`cid`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

-- Data exporting was unselected.

-- Dumping structure for table goonhub.clouddata
CREATE TABLE IF NOT EXISTS `clouddata` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ckey` text NOT NULL,
  `key` text NOT NULL,
  `value` text NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `ckey` (`ckey`(768))
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

-- Data exporting was unselected.

-- Dumping structure for table goonhub.cloudsaves
CREATE TABLE IF NOT EXISTS `cloudsaves` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ckey` mediumtext NOT NULL,
  `save_name` mediumtext NOT NULL COMMENT 'Used to identify for deletion',
  `save` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

-- Data exporting was unselected.

-- Dumping structure for table goonhub.connection
CREATE TABLE IF NOT EXISTS `connection` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ckey` tinytext DEFAULT NULL,
  `ip` bigint(20) DEFAULT NULL,
  `cid` bigint(20) DEFAULT NULL,
  `timestamp` datetime NOT NULL DEFAULT current_timestamp(),
  `initial` tinyint(4) NOT NULL DEFAULT 0 COMMENT 'First connection to a round?',
  `round` int(11) NOT NULL DEFAULT 0 COMMENT 'Round ID',
  PRIMARY KEY (`id`),
  KEY `ip` (`ip`),
  KEY `cid` (`cid`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

-- Data exporting was unselected.

-- Dumping structure for table goonhub.feedback-version
CREATE TABLE IF NOT EXISTS `feedback-version` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ckey` tinytext DEFAULT NULL,
  `agent` mediumtext DEFAULT NULL,
  `major` smallint(6) DEFAULT NULL,
  `minor` smallint(6) DEFAULT NULL,
  `server_uid` smallint(6) DEFAULT NULL,
  `server_id` tinytext DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `byond_version` (`major`,`minor`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

-- Data exporting was unselected.

-- Dumping structure for table goonhub.jobtracking
CREATE TABLE IF NOT EXISTS `jobtracking` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ckey` tinytext NOT NULL,
  `key` tinytext NOT NULL,
  `value` bigint(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

-- Data exporting was unselected.

-- Dumping structure for table goonhub.notes
CREATE TABLE IF NOT EXISTS `notes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `server_key` int(11) NOT NULL,
  `server_id` tinytext NOT NULL,
  `ckey` tinytext NOT NULL,
  `akey` tinytext NOT NULL,
  `note` longtext NOT NULL,
  `deleted` tinyint(4) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `ckey` (`ckey`(255))
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

-- Data exporting was unselected.

-- Dumping structure for table goonhub.participation
CREATE TABLE IF NOT EXISTS `participation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ckey` text NOT NULL,
  `record_type` text NOT NULL,
  `count` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `ckey` (`ckey`(768))
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

-- Data exporting was unselected.

-- Dumping structure for table goonhub.players
CREATE TABLE IF NOT EXISTS `players` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ckey` tinytext DEFAULT NULL,
  `last_ip` bigint(20) DEFAULT NULL,
  `last_cid` bigint(20) DEFAULT NULL,
  `firstseen` datetime DEFAULT NULL,
  `lastseen` datetime DEFAULT NULL,
  `playtime` bigint(20) NOT NULL DEFAULT 0,
  `flags` tinyint(3) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ckey` (`ckey`) USING HASH
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

-- Data exporting was unselected.

-- Dumping structure for table goonhub.rounds
CREATE TABLE IF NOT EXISTS `rounds` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `server_id` text NOT NULL,
  `server_key` text NOT NULL,
  `starting_station_name` text NOT NULL,
  `start_stamp` datetime NOT NULL,
  `ending_station_name` text DEFAULT NULL COMMENT 'Populated post-round',
  `end_stamp` datetime DEFAULT NULL COMMENT 'Populated post-round',
  `mode` text DEFAULT NULL COMMENT 'Populated post-round',
  `reason` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `jobban` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ckey` tinytext NOT NULL,
  `rank` text NOT NULL,
  `akey` tinytext NOT NULL,
  `server_id` tinytext DEFAULT NULL,
  `issue_time` datetime NOT NULL COMMENT 'Database Only',
  `remove_time` datetime DEFAULT NULL COMMENT 'Database Only',
  `removed` tinyint(4) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;


-- Data exporting was unselected.

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
