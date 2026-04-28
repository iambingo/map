-- MySQL dump 10.13  Distrib 8.0.46, for Linux (x86_64)
--
-- Host: localhost    Database: mapdb
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `mapdb`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `mapdb` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `mapdb`;

--
-- Table structure for table `asset_class_configs`
--

DROP TABLE IF EXISTS `asset_class_configs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `asset_class_configs` (
  `code` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '资产类别代码',
  `name` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '资产类别名称',
  `expected_return` float NOT NULL COMMENT '预期年化收益率',
  `expected_volatility` float NOT NULL COMMENT '预期年化波动率',
  `default_min_weight` float NOT NULL COMMENT '默认最低权重',
  `default_max_weight` float NOT NULL COMMENT '默认最高权重',
  `sort_order` smallint NOT NULL COMMENT '展示排序',
  `is_active` smallint NOT NULL DEFAULT '1' COMMENT '是否启用',
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键 ID',
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '最后更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '软删除标志 0=正常 1=已删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_asset_class_code` (`code`),
  KEY `ix_asset_class_configs_is_deleted` (`is_deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='资产类别配置表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `asset_class_configs`
--

LOCK TABLES `asset_class_configs` WRITE;
/*!40000 ALTER TABLE `asset_class_configs` DISABLE KEYS */;
/*!40000 ALTER TABLE `asset_class_configs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ic_meetings`
--

DROP TABLE IF EXISTS `ic_meetings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ic_meetings` (
  `meeting_code` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '会议编码，业务唯一键',
  `title` varchar(256) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '会议标题',
  `type` enum('FICC','MIXED') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '会议类型 FICC=固定收益 MIXED=混合',
  `status` enum('DRAFT','VOTING','PUBLISHED') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'DRAFT' COMMENT '会议状态 DRAFT→VOTING→PUBLISHED',
  `scheduled_at` datetime DEFAULT NULL COMMENT '计划召开时间（可空）',
  `created_by` bigint NOT NULL COMMENT '创建人 user_id（逻辑关联，无物理外键）',
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键 ID',
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '最后更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '软删除标志 0=正常 1=已删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_ic_meetings_meeting_code` (`meeting_code`),
  KEY `ix_ic_meetings_created_by` (`created_by`),
  KEY `ix_ic_meetings_status_deleted` (`status`,`is_deleted`),
  KEY `ix_ic_meetings_is_deleted` (`is_deleted`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='投委会会议主表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ic_meetings`
--

LOCK TABLES `ic_meetings` WRITE;
/*!40000 ALTER TABLE `ic_meetings` DISABLE KEYS */;
INSERT INTO `ic_meetings` VALUES ('TEST-001','test meeting','FICC','DRAFT',NULL,1,1,'2026-04-22 05:23:28','2026-04-22 05:23:28',0);
/*!40000 ALTER TABLE `ic_meetings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ic_mixed_questionnaire_submissions`
--

DROP TABLE IF EXISTS `ic_mixed_questionnaire_submissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ic_mixed_questionnaire_submissions` (
  `session_code` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '会期标识，如 2026Q2-MIXED-001；对前端透明，后端内部与 ic_meetings 关联',
  `submitter_id` bigint NOT NULL COMMENT '提交人 user_id（逻辑关联，无物理外键）',
  `status` enum('DRAFT','SUBMITTED') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'DRAFT' COMMENT '提交状态 DRAFT=草稿 SUBMITTED=已确认提交',
  `questionnaire_json` json NOT NULL COMMENT '资配观点结构化内容 JSON，含 section_a_allocation / section_b_macro / section_c_core_view / section_d_target_positions 等板块',
  `submitted_at` datetime DEFAULT NULL COMMENT '确认提交时间（DRAFT 状态下为空）',
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键 ID',
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '最后更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '软删除标志 0=正常 1=已删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_ic_mixed_qs_session_submitter` (`session_code`,`submitter_id`),
  KEY `ix_ic_mixed_questionnaire_submissions_is_deleted` (`is_deleted`),
  KEY `ix_ic_mixed_qs_submitter_id` (`submitter_id`),
  KEY `ix_ic_mixed_qs_session_code` (`session_code`),
  KEY `ix_ic_mixed_qs_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='混合投委会会前筹备问卷提交记录，每人每场会期唯一';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ic_mixed_questionnaire_submissions`
--

LOCK TABLES `ic_mixed_questionnaire_submissions` WRITE;
/*!40000 ALTER TABLE `ic_mixed_questionnaire_submissions` DISABLE KEYS */;
INSERT INTO `ic_mixed_questionnaire_submissions` VALUES ('2026Q2',1,'SUBMITTED','{\"section_a\": {\"债券\": 4, \"权益-红利\": 4, \"权益-成长\": 3, \"权益-价值\": 4, \"黄金\": 5, \"原油\": 2}, \"section_b\": {\"债券\": true, \"权益-红利\": false, \"权益-成长\": false, \"权益-价值\": false, \"黄金\": true, \"原油\": false}, \"section_c\": [\"利率债\", \"黄金\", \"REITs\"], \"core_view\": \"利率下行趋势下债券配置价值提升，建议增加久期。黄金作为避险资产在地缘不确定性下具备配置价值。\", \"risk_flag\": false}','2026-04-22 05:31:06',1,'2026-04-22 03:21:33','2026-04-22 05:31:05',0),('2026Q2',2,'SUBMITTED','{\"section_a\": {\"债券\": 3, \"权益-红利\": 4, \"权益-成长\": 4, \"权益-价值\": 3, \"黄金\": 3, \"原油\": 3}, \"section_b\": {\"债券\": false, \"权益-红利\": true, \"权益-成长\": true, \"权益-价值\": false, \"黄金\": false, \"原油\": false}, \"section_c\": [\"可转债\", \"港股\", \"A股大盘\"], \"core_view\": \"A股市场结构性机会明确，科技与红利板块值得重点关注。港股估值优势明显，建议通过沪港通适度增配。\", \"risk_flag\": false}','2026-04-22 05:29:43',2,'2026-04-22 05:29:43','2026-04-22 05:29:43',0),('2026Q2',3,'SUBMITTED','{\"section_a\": {\"债券\": 5, \"权益-红利\": 2, \"权益-成长\": 2, \"权益-价值\": 3, \"黄金\": 5, \"原油\": 3}, \"section_b\": {\"债券\": true, \"权益-红利\": false, \"权益-成长\": false, \"权益-价值\": false, \"黄金\": true, \"原油\": false}, \"section_c\": [\"利率债\", \"信用债\"], \"core_view\": \"地缘风险仍存，维持均衡配置，债券防御价值突出。信用利差处于历史低位需警惕信用事件风险。\", \"risk_flag\": true}','2026-04-22 05:30:00',3,'2026-04-22 03:21:33','2026-04-22 05:30:00',0);
/*!40000 ALTER TABLE `ic_mixed_questionnaire_submissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ic_resolutions`
--

DROP TABLE IF EXISTS `ic_resolutions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ic_resolutions` (
  `meeting_id` bigint NOT NULL COMMENT '会议 ID（逻辑关联，无物理外键）',
  `aggregated_taa` json NOT NULL COMMENT '聚合后的最终资产配置指引 JSON',
  `ai_minutes` text COLLATE utf8mb4_unicode_ci COMMENT 'AI 生成会议纪要（异步生成，初始为空）',
  `published_at` datetime DEFAULT NULL COMMENT '决议发布时间',
  `published_by` bigint DEFAULT NULL COMMENT '发布操作人 user_id（逻辑关联，无物理外键）',
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键 ID',
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '最后更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '软删除标志 0=正常 1=已删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_ic_resolutions_meeting_id` (`meeting_id`),
  KEY `ix_ic_resolutions_is_deleted` (`is_deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='投委会决议，每场会议唯一，由计票聚合写入';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ic_resolutions`
--

LOCK TABLES `ic_resolutions` WRITE;
/*!40000 ALTER TABLE `ic_resolutions` DISABLE KEYS */;
/*!40000 ALTER TABLE `ic_resolutions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ic_vote_records`
--

DROP TABLE IF EXISTS `ic_vote_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ic_vote_records` (
  `meeting_id` bigint NOT NULL COMMENT '会议 ID（逻辑关联，无物理外键）',
  `user_id` bigint NOT NULL COMMENT '投票人 user_id（逻辑关联，无物理外键）',
  `vote_json` json NOT NULL COMMENT '投票内容 JSON：choice_items（众数项）+ numeric_items（均值项）',
  `submitted_at` datetime DEFAULT NULL COMMENT '投票提交时间',
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键 ID',
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '最后更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '软删除标志 0=正常 1=已删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_ic_vote_records_meeting_user` (`meeting_id`,`user_id`),
  KEY `ix_ic_vote_records_is_deleted` (`is_deleted`),
  KEY `ix_ic_vote_records_user_id` (`user_id`),
  KEY `ix_ic_vote_records_meeting_id` (`meeting_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='投委会投票记录，每人每场会议唯一';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ic_vote_records`
--

LOCK TABLES `ic_vote_records` WRITE;
/*!40000 ALTER TABLE `ic_vote_records` DISABLE KEYS */;
/*!40000 ALTER TABLE `ic_vote_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pending_commands`
--

DROP TABLE IF EXISTS `pending_commands`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pending_commands` (
  `command_type` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '指令类型，如 SUBMIT_SAA_FOR_APPROVAL / TRIGGER_PORTFOLIO_REBALANCE',
  `idempotency_key` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '幂等键，全局唯一，防止重复投递',
  `user_id` bigint NOT NULL COMMENT '发起人 user_id',
  `payload` json NOT NULL COMMENT '指令业务参数 JSON',
  `status` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'PENDING' COMMENT '指令状态 PENDING→PROCESSING→DONE/FAILED',
  `dispatch_mode` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'MQ' COMMENT '分发模式：MQ=异步消息队列 SYNC=同步 Adapter 调用',
  `result` json DEFAULT NULL COMMENT '执行结果摘要（成功返回值或失败错误信息）',
  `error_message` text COLLATE utf8mb4_unicode_ci COMMENT '失败时的错误详情',
  `retry_count` bigint NOT NULL DEFAULT '0' COMMENT '已重试次数',
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键 ID',
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '最后更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '软删除标志 0=正常 1=已删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_pending_commands_idempotency_key` (`idempotency_key`),
  KEY `ix_pending_commands_user_id` (`user_id`),
  KEY `ix_pending_commands_is_deleted` (`is_deleted`),
  KEY `ix_pending_commands_status` (`status`,`is_deleted`),
  KEY `ix_pending_commands_command_type` (`command_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='跨域指令登记表，保障幂等与全链路可追溯';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pending_commands`
--

LOCK TABLES `pending_commands` WRITE;
/*!40000 ALTER TABLE `pending_commands` DISABLE KEYS */;
/*!40000 ALTER TABLE `pending_commands` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `saa_drafts`
--

DROP TABLE IF EXISTS `saa_drafts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `saa_drafts` (
  `user_id` bigint NOT NULL COMMENT '创建人 user_id',
  `version` bigint NOT NULL COMMENT '版本号',
  `risk_level` smallint NOT NULL COMMENT '风险等级 1-5',
  `total_amount` float NOT NULL COMMENT '总配置金额（万元）',
  `weights` json NOT NULL COMMENT '资产类别权重',
  `expected_return` float DEFAULT NULL COMMENT '预期年化收益率',
  `expected_volatility` float DEFAULT NULL COMMENT '预期年化波动率',
  `constraints` json NOT NULL COMMENT '约束条件',
  `status` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'DRAFT' COMMENT '草稿状态',
  `reject_reason` text COLLATE utf8mb4_unicode_ci COMMENT '审批拒绝原因',
  `approver_id` bigint DEFAULT NULL COMMENT '审批人 user_id',
  `notes` text COLLATE utf8mb4_unicode_ci COMMENT '备注说明',
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键 ID',
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '最后更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '软删除标志 0=正常 1=已删除',
  PRIMARY KEY (`id`),
  KEY `ix_saa_drafts_version` (`user_id`,`version`),
  KEY `ix_saa_drafts_is_deleted` (`is_deleted`),
  KEY `ix_saa_drafts_user_status` (`user_id`,`status`,`is_deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='SAA 战略资产配置草稿表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `saa_drafts`
--

LOCK TABLES `saa_drafts` WRITE;
/*!40000 ALTER TABLE `saa_drafts` DISABLE KEYS */;
/*!40000 ALTER TABLE `saa_drafts` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-22  5:36:49
