-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: mall
-- ------------------------------------------------------
-- Server version	8.0.41

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
-- Table structure for table `answers`
--

DROP TABLE IF EXISTS `answers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `answers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `inquiry_id` int DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  `content` text COLLATE utf8mb4_general_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `inquiry_id` (`inquiry_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `answers_ibfk_1` FOREIGN KEY (`inquiry_id`) REFERENCES `inquiries` (`id`),
  CONSTRAINT `answers_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `answers`
--

LOCK TABLES `answers` WRITE;
/*!40000 ALTER TABLE `answers` DISABLE KEYS */;
INSERT INTO `answers` VALUES (1,8,1,'안녕하세요','2025-04-26 00:28:33','2025-04-26 00:28:33'),(2,8,1,'안녕하세요ㅇㄴㅁ','2025-04-26 00:28:51','2025-04-26 00:28:51'),(3,13,1,'답변','2025-04-26 00:29:59','2025-04-26 00:37:52');
/*!40000 ALTER TABLE `answers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `carts`
--

DROP TABLE IF EXISTS `carts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `carts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_cart_user_product` (`user_id`,`product_id`),
  KEY `fk_carts_products` (`product_id`),
  CONSTRAINT `fk_carts_products` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `fk_carts_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `carts`
--

LOCK TABLES `carts` WRITE;
/*!40000 ALTER TABLE `carts` DISABLE KEYS */;
/*!40000 ALTER TABLE `carts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'남성','2025-04-23 00:33:54','2025-04-23 00:33:54'),(2,'여성','2025-04-23 00:33:54','2025-04-23 00:33:54');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `category_types`
--

DROP TABLE IF EXISTS `category_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `category_types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `category_id` int NOT NULL,
  `name` varchar(50) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_category_types_categories` (`category_id`),
  CONSTRAINT `fk_category_types_categories` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `category_types`
--

LOCK TABLES `category_types` WRITE;
/*!40000 ALTER TABLE `category_types` DISABLE KEYS */;
INSERT INTO `category_types` VALUES (1,1,'상의','2025-04-23 00:34:10','2025-04-23 00:34:10'),(2,1,'하의','2025-04-23 00:34:10','2025-04-23 00:34:10'),(3,1,'아우터','2025-04-23 00:34:10','2025-04-23 00:34:10'),(4,1,'신발','2025-04-23 00:34:10','2025-04-23 00:34:10'),(5,2,'상의','2025-04-23 00:34:10','2025-04-23 00:34:10'),(6,2,'하의','2025-04-23 00:34:10','2025-04-23 00:34:10'),(7,2,'아우터','2025-04-23 00:34:10','2025-04-23 00:34:10'),(8,2,'신발','2025-04-23 00:34:10','2025-04-23 00:34:10'),(9,2,'원피스','2025-04-23 00:34:10','2025-04-23 00:34:10'),(10,2,'스커트','2025-04-23 00:34:10','2025-04-23 00:34:10');
/*!40000 ALTER TABLE `category_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inquiries`
--

DROP TABLE IF EXISTS `inquiries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inquiries` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `type` enum('NOTICE','FAQ','QNA') DEFAULT 'QNA',
  `title` varchar(200) DEFAULT NULL,
  `content` text,
  `image_path` varchar(255) DEFAULT NULL,
  `answer` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_inquiries_users` (`user_id`),
  CONSTRAINT `fk_inquiries_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inquiries`
--

LOCK TABLES `inquiries` WRITE;
/*!40000 ALTER TABLE `inquiries` DISABLE KEYS */;
INSERT INTO `inquiries` VALUES (1,12,'QNA','갑수형','갑수형 ','inquiries_image/1.avif',NULL,'2025-04-23 05:42:51','2025-04-23 05:42:51'),(2,16,'QNA','동혁아 뭐하니','시험공부해라',NULL,NULL,'2025-04-25 11:04:52','2025-04-25 11:04:52'),(4,16,'QNA','갑수형 여기 폰트가 이상해요','빠르게 바꿔주세요',NULL,NULL,'2025-04-25 11:09:17','2025-04-25 11:09:17'),(6,1,'QNA','dsa','dsadd','./static/inquiries_image/6.jpg',NULL,'2025-04-25 11:14:47','2025-04-25 11:25:48'),(7,1,'QNA','dsad','dsad','./static/inquiries_image/7.jpg',NULL,'2025-04-25 11:27:29','2025-04-25 11:27:29'),(8,1,'QNA','dsadsa','dsaddsad','./static/inquiries_image/8.jpg',NULL,'2025-04-25 11:27:44','2025-04-25 11:27:44'),(13,1,'QNA','sads','dsda','inquiries_image/13.jpg',NULL,'2025-04-26 00:21:29','2025-04-26 00:21:29'),(16,19,'QNA','test','qweasd','inquiries_image/16',NULL,'2025-04-26 08:03:33','2025-04-26 08:03:33'),(17,1,'QNA','dsa','dsa','inquiries_image/17.png',NULL,'2025-04-26 08:14:30','2025-04-26 08:14:30');
/*!40000 ALTER TABLE `inquiries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_items`
--

DROP TABLE IF EXISTS `order_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity` int DEFAULT NULL,
  `unit_price` decimal(10,2) DEFAULT NULL,
  `subtotal` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_order_items_orders` (`order_id`),
  KEY `fk_order_items_products` (`product_id`),
  CONSTRAINT `fk_order_items_orders` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  CONSTRAINT `fk_order_items_products` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
INSERT INTO `order_items` VALUES (29,24,22,3,7900.00,NULL),(30,25,45,1,55900.00,NULL),(31,25,44,1,89900.00,NULL);
/*!40000 ALTER TABLE `order_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `address` varchar(255) NOT NULL,
  `payment_method` varchar(50) NOT NULL,
  `total_amount` decimal(10,2) DEFAULT NULL,
  `status` enum('PENDING','PAID','SHIPPED','DELIVERED','CANCELLED') NOT NULL DEFAULT 'PENDING',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_orders_users` (`user_id`),
  CONSTRAINT `fk_orders_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (24,1,'강원특별자치도 홍천군 화촌면 옻나무여울길 1 외삼포리 dsa','card',23700.00,'PAID','2025-04-25 08:28:31','2025-04-25 11:13:26'),(25,16,'부산 강서구 르노삼성대로 14 신호동 한라 102동 304호','bank',145800.00,'PENDING','2025-04-25 11:03:55','2025-04-25 11:03:55');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `amount` decimal(10,2) DEFAULT NULL,
  `method` varchar(50) DEFAULT NULL,
  `status` enum('PENDING','COMPLETED','FAILED') DEFAULT 'PENDING',
  `transaction_id` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_payments_orders` (`order_id`),
  CONSTRAINT `fk_payments_orders` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments`
--

LOCK TABLES `payments` WRITE;
/*!40000 ALTER TABLE `payments` DISABLE KEYS */;
/*!40000 ALTER TABLE `payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_images`
--

DROP TABLE IF EXISTS `product_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_images` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int NOT NULL,
  `url` varchar(255) NOT NULL,
  `is_primary` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `fk_product_images_products` (`product_id`),
  CONSTRAINT `fk_product_images_products` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=78 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_images`
--

LOCK TABLES `product_images` WRITE;
/*!40000 ALTER TABLE `product_images` DISABLE KEYS */;
INSERT INTO `product_images` VALUES (4,4,'4793563_17398642281902_big.png.webp',1),(5,5,'4759463_17387453674182_big.jpg.webp',1),(6,6,'4694287_17376975288373_big.jpg.webp',1),(7,7,'2035586_1_big.jpg.webp',1),(9,9,'4790079_17439814625490_big.jpg.webp',1),(12,12,'4427040_17385582052466_big.jpg.webp',1),(15,15,'4706584_17425210611185_big.jpg.webp',1),(19,19,'2496150_2_big.jpg.webp',1),(22,22,'4268396_17217141101278_big.jpg.webp',1),(34,34,'e38ac8716d32416dad65a162257a4218.jpg',1),(36,36,'9231dbac1d9448b099897384658652ae.jpg',1),(37,37,'7f253bed55fe4dcb8479bc4ec0b57fdc.jpg',1),(38,38,'7a342aa186d242b09ff11801d135a0d4.jpg',1),(39,39,'8943a1a13a1043908399b3313bdf1649.jpg',1),(40,40,'a8b978a18a4449a9bea4729f3b44630a.jpg',1),(41,41,'0cc456d7339b4ed1849cac2734f6a7c5.jpg',1),(42,42,'f5e88550948a4707a5d194da3da7ee8a.jpg',1),(43,43,'007f619027dd40cc8524003a557659ce.jpg',1),(44,44,'ec11bf3ed11c45c284be258c8bb56797.jpg',1),(45,45,'a18587e759914be79f4751d6c5b56cb1.jpg',1),(46,46,'d0e232788e0b45d8be730f2417b13b50.webp',1),(47,47,'fd84994023ba430aad1efb5b1b4e77a8.webp',1),(48,48,'82c2b69225bd420aa166fe07bb7fa93b.webp',1),(49,49,'f05aec5f0311417f8e3075c76de8a466.webp',1),(50,50,'10c0f534870b44139b2115bc633636ca.webp',1),(51,51,'28548eb333824c3b951b8dfda7c52cdb.webp',1),(52,52,'e63e0274112e41718ee2ebe351d52dc3.webp',1),(53,53,'94e8a15b337046889e97bd01d3e8572b.webp',1),(54,54,'5b2d4ba337c64b56b9dec5c1eedbd4c9.webp',1),(55,55,'c0bf8613d00043e890f6a24e7e488c0b.webp',1),(56,56,'31f55377c43c419890e862a7d0d12676.webp',1),(57,57,'330006fd29704eb1a64cb018dfde995a.webp',1),(58,58,'80d92e336a174ab58490c341fd64e4aa.webp',1),(59,59,'b4081c0c473a476389e6507c95bbf4d6.webp',1),(60,60,'b29d6797327a491c85af3c67400903fc.webp',1),(61,61,'9d802e662c07440f8308f59a3caf3a11.webp',1),(62,62,'d86d3f633ad44f7ebfa8160c39fc9b9a.webp',1),(63,63,'329f9238dceb4236bac391e54aec615d.webp',1),(64,64,'a7f39e38720f40adaeb721c95a83832b.webp',1),(65,65,'d47d89502cc8473bbde62ce1c5443d6d.webp',1),(66,66,'3555aed31f224f6689d27f4ea38ca3b5.webp',1),(68,68,'b90c4ebdd0b3450b914fbd8852a5499b.jpg',1),(69,69,'dcebb4fda8a0433f8ac15b95a816d2ff.jpg',1),(70,70,'37e23530435b4d57ab467797ae65800e.jpg',1),(71,71,'0a656847e01c48aba5e136a2dbec99f9.jpg',1),(72,72,'c5c81a90e4fd457c8adc27ef6965b8c4.jpg',1),(73,73,'4738058b999b45eba7ee9bd8752edb18.jpg',1),(74,74,'a179e639fa0f45a3935789b66551357d.jpg',1),(75,75,'302d0db97e0f4e1282102c3b41ff983d.jpg',1),(76,76,'daa38ae45a3b4ca18bbf67d7c47f8ae4.jpg',1),(77,77,'1f8497a16be04b299d52cd0f80062f6e.jpg',1);
/*!40000 ALTER TABLE `product_images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_variants`
--

DROP TABLE IF EXISTS `product_variants`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_variants` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int NOT NULL,
  `size` enum('S','M','L','XL') NOT NULL,
  `stock_quantity` int DEFAULT '0',
  `price` decimal(10,2) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_product_variants_products` (`product_id`),
  CONSTRAINT `fk_product_variants_products` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_variants`
--

LOCK TABLES `product_variants` WRITE;
/*!40000 ALTER TABLE `product_variants` DISABLE KEYS */;
/*!40000 ALTER TABLE `product_variants` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `id` int NOT NULL AUTO_INCREMENT,
  `category_type_id` int NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` text,
  `price` decimal(10,2) DEFAULT NULL,
  `stock_quantity` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_products_category_types` (`category_type_id`),
  CONSTRAINT `fk_products_category_types` FOREIGN KEY (`category_type_id`) REFERENCES `category_types` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=78 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (4,5,'VINTAGE FRINGE KNIT (IVORY)','품번\r\nZ5S-VTGFRGKN30\r\n성별\r\n여\r\n시즌\r\n2025 SS\r\n조회수\r\n2.3만 회 이상 (최근 1개월)',133000.00,50,'2025-04-24 08:35:22','2025-04-24 08:35:22'),(5,5,'우먼 케이블 크롭 니트 버터','품번\r\nLE2402KT63BT\r\n성별\r\n여\r\n조회수\r\n2천 회 이상 (최근 1개월)',55050.00,30,'2025-04-24 08:36:56','2025-04-24 08:36:56'),(6,5,'데미지드 브이넥 리브드 니트 [스킨 핑크]','∴제품 실측\r\n\r\nOS 총장 60 cm 어깨너비 28 cm 가슴단면 31 cm 소매길이 64 cm\r\n\r\n모델 171cm OS 사이즈 착용\r\n\r\n주문 전 실측을 꼭 참고 부탁드리겠습니다.\r\n\r\n∴제품 설명\r\n\r\n데미지드 브이넥 리브드 니트 스킨 핑크 버전입니다.\r\n과하지 않은 데미지드 디테일과 소매 은니브시 버튼 포인트로\r\n그런지한 락시크 무드를 연출할 수 있습니다.\r\n깊지 않은 V넥 디자인으로 넥 라인을 드러낼 수 있고,\r\n잔잔한 립 조직이 볼륨감 있으면서도 슬림한 바디 라인을 만들어 줍니다.\r\n폴리에스터 & 나일론 혼방 니트로 내구성과 탄력성이 좋아 편하게 착용할 수 있습니다.\r\n웨이스트 랭스, 타이트 핏 가먼트입니다.\r\n\r\n∴세탁방법\r\n\r\n드라이클리닝\r\n\r\n∴교환 반품이 불가한 경우\r\n\r\n교환/반품 기간이 경과 했을 경우(상품 수령일로부터 주말, 공휴일을 제외한 7일 이내)\r\n패키지 구성품 (예-옷걸이, 수트케이스, 쇼핑백, 스페셜 쿠폰 카드 등) 누락 및 제품의 Tag이 제거된 경우\r\n반품이 가능하지 않다는 조건에 소비자가 동의한 경우\r\n흰색 의류, 니트, 티 등 시험 착용만으로 늘어짐 및 오염이 생기는 의류의 경우\r\n세탁 및 착용 흔적, 의도적인 상품훼손 등으로 인해 상품 가치가 하락한 경우',52000.00,40,'2025-04-24 08:37:51','2025-04-24 08:37:51'),(7,5,'U 넥 세미 크롭 니트 티셔츠 베이지','U넥세미크롭니트티셔츠\r\nU NECK SEMI-CROP KNIT T-SHIRT\r\n린넨혼방소재로가볍게착용하기좋은니트티셔츠입니다. 신축성또한좋아서착용시편안한활동이가능하며,\r\n루즈핏실루엣과세미크롭디자인으로어느하의에매치하여도좋습니다.\r\n시스루골지형태의U넥으로이너와함께착용권장합니다.',14500.00,48,'2025-04-24 08:38:51','2025-04-24 08:38:51'),(9,5,'1911 트랙탑(FS2FTH1155FDNA)','품번\r\n1100FS2FTH1155FDNA\r\n성별\r\n여\r\n조회수\r\n8.7천 회 이상 (최근 1개월)',109000.00,34,'2025-04-24 08:42:20','2025-04-24 08:42:20'),(12,5,'노라 투웨이 버튼 가디건 [FOREST]','품번\r\nZ24FOT10FO\r\n성별\r\n여\r\n시즌\r\n2024 FW\r\n조회수\r\n6.8천 회 이상 (최근 1개월)\r\n누적판매\r\n3.7천 개 이상',33600.00,33,'2025-04-24 08:43:16','2025-04-24 08:43:16'),(15,5,'유니온 스트라이프 카라 티-스카이 블루','품번\r\nB252TS04SB\r\n성별\r\n여\r\n조회수\r\n5.9만 회 이상 (최근 1개월)',71100.00,22,'2025-04-24 08:44:24','2025-04-24 08:44:24'),(19,5,'W 윔블던 코튼 저지 티셔츠 - 화이트','품번\r\nWMPOKNINCU20441-100\r\n성별\r\n여\r\n시즌\r\n2022 SS\r\n조회수\r\n9.7천 회 이상 (최근 1개월)',119000.00,22,'2025-04-24 08:45:51','2025-04-24 08:45:51'),(22,5,'모달 코튼 레터링 반팔 티블라우스','품번\r\n5012195429\r\n성별\r\n여\r\n시즌\r\n2023 SS\r\n조회수\r\n5.8천 회 이상 (최근 1개월)',7900.00,56,'2025-04-24 08:47:34','2025-04-24 08:47:34'),(34,1,'긴팔 우븐 스케이트보딩 탑','1r1rwqr',69000.00,1,'2025-04-25 05:12:36','2025-04-25 05:12:36'),(36,9,'패턴 미니 원피스','테슬 디테일 코드 장식 브이넥 긴소매 미니 원피스. 프릴 가공 밑단.',59900.00,5,'2025-04-25 10:27:27','2025-04-25 10:27:27'),(37,9,'린넨 셔츠형 원피스','리넨 소재로 제작된 튜닉 스타일 원피스. 플랩오버 칼라 브이넥, 버클과 버튼으로 마감된 팔꿈치 아래 길이의 소매. 앞면 패치 포켓. 옆면 밑단 절개. 앞면 버튼 여밈.',89900.00,6,'2025-04-25 10:27:58','2025-04-25 10:27:58'),(38,9,'리넨 미디 원피스','리넨 소재로 제작된 원피스입니다. 스퀘어넥 슬리브리스 디자인. 앞면 페이크 버튼 디테일, 밑단 절개. 뒷면 스티치 부분 콘솔 지퍼 여밈.',89900.00,6,'2025-04-25 10:28:24','2025-04-25 10:28:24'),(39,9,'크레이프 벨트 미디 원피스','라운드넥 슬리브리스 원피스. 장식용 버튼과 골드 장식이 달린 앞면 엘라스틱 벨트 디테일. 플랩오버 디자인의 앞면 패치 포켓. 앞면 트임이 있는 밑단. 뒷면 심라인 히든 지퍼로 여밈.',89900.00,10,'2025-04-25 10:29:23','2025-04-25 10:29:23'),(40,9,'러스틱 미디 원피스','크로스 브이넥 및 암홀 슬리브리스 미디 원피스. 버클로 조절 가능한 동일 소재 벨트. 플로럴 자카드 디테일.',57900.00,6,'2025-04-25 10:30:14','2025-04-25 10:30:14'),(41,9,'ZW 컬렉션 포플린 셔츠 원피스','면 방적 소재로 제작된 원피스. 플랩 칼라 및 반소매 디자인. 가슴 부분 플랩 패치 포켓. 같은 소재의 벨트는 리본 매듭으로 조절 가능. 플랩오버 안쪽 히든 버튼으로 여미는 앞면.',109900.00,6,'2025-04-25 10:30:51','2025-04-25 10:30:51'),(42,9,'벨트 패턴 미디 원피스','라펠 칼라 브이넥 긴소매 원피스, 버클과 버튼이 달린 롤업 마감. 벨트 디테일. 스티치에 숨겨진 옆면 포켓. 옆면 절개 밑단. 앞면 버튼 여밈.',89900.00,8,'2025-04-25 10:31:13','2025-04-25 10:31:13'),(43,9,'린넨 톱스티칭 미니 원피스','리넨 소재로 제작된 원피스. 라운드넥 슬리브리스. 배색 톱스티칭 디테일. 앞면 버튼 여밈.',59900.00,123,'2025-04-25 10:31:35','2025-04-25 10:31:35'),(44,9,'벨트 새틴 원피스','크로스 브이넥 라펠 칼라 긴소매 미디 원피스. 신축성 있는 허리와 벨트.',89900.00,21,'2025-04-25 10:31:58','2025-04-25 10:31:58'),(45,9,'슬림핏 솔리드 니트 미디 원피스','\r\n라운드넥 반소매 미디 원피스.',55900.00,23,'2025-04-25 10:32:25','2025-04-25 10:32:25'),(46,5,'[3PACK] 버튼업 니트','품번\r\n2035380984\r\n성별\r\n여\r\n시즌\r\n2024 FW\r\n조회수\r\n5.7천 회 이상 (최근 1개월)',45000.00,22,'2025-04-26 00:41:49','2025-04-26 00:41:49'),(47,10,'우먼즈 크링클 롱 스커트 [베이지]','품번\r\nMWCKS204-BE\r\n성별\r\n여\r\n시즌\r\n2023 SS\r\n조회수\r\n1만 회 이상 (최근 1개월)\r\n크링클 원단의 빈티지 워싱 가공이 돋보이는 우먼즈 크링클 롱 스커트입니다.\r\n맥시한 길이감으로 다양한 룩에 활용할 수 있습니다. 허리 밴드를 생략해 미니멀하게 디자인했고 시원한 촉감으로 더운 여름에도 부담 없이 착용할 수 있습니다. 동일 원단을 사용한 우먼즈 크링클 칼라리스 반팔 재킷과 셋업으로 연출할 수 있습니다.',37290.00,47,'2025-04-26 00:42:57','2025-04-26 00:42:57'),(48,10,'호안 핀턱 롱 스커트','품번\r\n95573\r\n성별\r\n여\r\n조회수\r\n1.7만 회 이상 (최근 1개월)\r\n- 코튼100%\r\n- FREE(55~77)\r\n\"롱한 기장감으로 사랑스러운 맥시 플레어 스커트\"\r\n- 움직임에 따라 살랑이는 풍성한 훌 실루엣\r\n- 하단부분 핀턱 디테일로 담백한 포인트\r\n- 쾌적하고 탄탄한 코튼100%\r\n- 뒤틀림 없는 촘촘한 스티치로 편안한 안정적인 허리밴딩\r\n- 비침 방지를 위해 밀도있는 부드러운 안감\r\n- 러블리함이 가미된 캐주얼한 분위기로 S/S시즌 트렌드 아이템\r\n- [ SHAA 모델] 168cm / 55 size / 하의 26',59800.00,146,'2025-04-26 00:44:01','2025-04-26 00:44:01'),(49,10,'리트 플레어 롱 스커트','품번\r\nkoznok\r\n성별\r\n여\r\n조회수\r\n3.0천 회 이상 (최근 1개월)\r\n3월8일 순차 출고 !',44000.00,345,'2025-04-26 00:44:54','2025-04-26 00:44:54'),(50,10,'카고 데님 맥시 스웨트 스커트 라이트 블루','품번\r\nTRTHAASK02WB3\r\n성별\r\n여\r\n조회수\r\n3.8천 회 이상 (최근 1개월)',17800.00,33,'2025-04-26 00:45:56','2025-04-26 00:45:56'),(51,10,'블룸 트리플 핀턱 롱 스커트 ( 화이트 )','품번\r\n3241SK205410S\r\n성별\r\n여\r\n시즌\r\n2024 SS\r\n조회수\r\n1.9천 회 이상 (최근 1개월)',89300.00,55,'2025-04-26 00:47:00','2025-04-26 00:47:00'),(52,10,'Shirring Tiered Banding Skirts (White)','품번\r\n5006853384\r\n성별\r\n여\r\n조회수\r\n3천 회 이상 (최근 1개월)',87400.00,36,'2025-04-26 00:48:01','2025-04-26 00:48:01'),(53,10,'스머프 나일론 스트링 롱스커트_(2 colors)','품번\r\nS2306UCPBSK002\r\n성별\r\n여\r\n시즌\r\n2023 SS\r\n조회수\r\n4.0천 회 이상 (최근 1개월)',45000.00,68,'2025-04-26 00:49:10','2025-04-26 00:49:10'),(54,10,'Pumpkin Banding Skirt Blue check','품번\r\nRS0113\r\n성별\r\n여\r\n시즌\r\n2025 SS\r\n조회수\r\n5.4천 회 이상 (최근 1개월)',59200.00,78,'2025-04-26 00:49:53','2025-04-26 00:49:53'),(55,10,'Sheer Jovian Wrap Skirt (FL-240_Black)','품번\r\nFL-240_Black\r\n성별\r\n여\r\n시즌\r\n2025 ALL\r\n조회수\r\n4.4천 회 이상 (최근 1개월)\r\n허리 사이즈는 끈으로 묶는 형태라서 실측 무의미 합니다.',34400.00,33,'2025-04-26 00:50:52','2025-04-26 00:50:52'),(56,10,'셔링 프릴 롱 스커트_화이트','품번\r\n24SS009WH\r\n성별\r\n여\r\n조회수\r\n1.4천 회 이상 (최근 1개월)',82000.00,46,'2025-04-26 00:51:36','2025-04-26 00:51:36'),(57,8,'Float maryjane sandals (3color)','품번\r\n5015008920\r\n성별\r\n여\r\n조회수\r\n1.6만 회 이상 (최근 1개월)',116100.00,33,'2025-04-26 00:54:45','2025-04-26 00:54:45'),(58,8,'[CTBRZ X YASE] 스파이더 레더 스니커즈_SILVER','품번\r\nCTG2SH01SL\r\n성별\r\n여\r\n조회수\r\n3.3천 회 이상 (최근 1개월)',127200.00,24,'2025-04-26 00:55:37','2025-04-26 00:55:37'),(59,8,'[Archivepke x Ribbonbit] Platform sneakers(Nylon Black)','Archivépke\r\n[배송일정안내]\r\n360사이즈>4/25(금)순차배송\r\n370&380사이즈>즉시배송\r\n*최대한빠르게배송될수있도록최선을다하겠습니다.',279000.00,45,'2025-04-26 00:56:41','2025-04-26 00:56:41'),(60,8,'드리프트 운동화','품번\r\n5014581248\r\n성별\r\n공용\r\n시즌\r\n2025 SS\r\n조회수\r\n3.5천 회 이상 (최근 1개월)',45900.00,45,'2025-04-26 00:57:29','2025-04-26 00:57:29'),(61,8,'플리에 백 리본 스니커즈 3color','품번\r\nK25-SH001\r\n성별\r\n여\r\n시즌\r\n2025 SS\r\n조회수\r\n6.5천 회 이상 (최근 1개월)\r\n안녕하세요. 현재 주문량 증가로 인하여\r\n실버 색상 230, 235, 240 사이즈의 경우 5월 15일 재입고 되어 5월 19일 일괄 출고될 예정입니다.\r\n구매시 참고 부탁드리며, 입고 일이 당겨질 경우 안내드린 일정보다 빠르게 배송될 수도 있는 점 참고 부탁드립니다.',99000.00,12,'2025-04-26 00:59:43','2025-04-26 00:59:43'),(62,8,'ALPE DI SIUSI - BROWN','품번\r\nP00000BH\r\n성별\r\n여\r\n조회수\r\n2.6만 회 이상 (최근 1개월)',69900.00,67,'2025-04-26 01:01:32','2025-04-26 01:01:32'),(63,8,'[리퍼브] 오즈 스트랩 스니커즈 [n5270]_2color','OUTLET REFURB\r\n본상품은리퍼브(Refurb)상품입니다. 환경적가치를고려한합리적인쇼핑\r\n새상품못지않은리퍼브상품을만나보세요.\r\nCHECK POINT\r\n리퍼브상품이란? -사용시문제가없는상품으로선별되어발송되는\r\n샘플상품•반품상품전시상품등을뜻합니다',23000.00,23,'2025-04-26 01:02:33','2025-04-26 01:02:33'),(64,8,'[이시안 pick][이렌] 드라이빙 스니커즈 - 2color','품번\r\nJLSO5E440BK JLSO5F441SV\r\n성별\r\n여\r\n시즌\r\n2025 ALL\r\n조회수\r\n1만 회 이상 (최근 1개월)',100300.00,65,'2025-04-26 01:03:43','2025-04-26 01:03:43'),(65,8,'Racer 레이서 스니커즈 AHNK003','품번\r\n5006856138\r\n성별\r\n여\r\n조회수\r\n1.3천 회 이상 (최근 1개월)',76300.00,67,'2025-04-26 01:05:03','2025-04-26 01:05:03'),(66,8,'Cooing 4Color 메리제인 벨크로 스니커즈 3.5Cm','품번\r\nCooing\r\n성별\r\n여\r\n시즌\r\n2023 ALL\r\n조회수\r\n9.8천 회 이상 (최근 1개월)\r\n누적판매\r\n1.3천 개 이상',73650.00,56,'2025-04-26 01:06:11','2025-04-26 01:06:11'),(68,7,'브라운 에디나 스웨이드 재킷','고트스킨 스웨이드 재킷.\r\n\r\n· 퀼팅 브이넥 및 밑단\r\n· 지퍼 여밈\r\n· 웰트 포켓\r\n· 옆면 및 소맷단에 레이스업 여밈\r\n· 신축성 있는 비스코스 트윌 전체 안감',256500.00,123,'2025-04-26 02:25:49','2025-04-26 02:25:49'),(69,7,'블랙 시그니처 시어링 재킷','두꺼운 그레인 램스킨 재킷. 오프 화이트 색상의 시어링 트리밍.\r\n\r\n· 패널 구조\r\n· 퍼넬넥\r\n· 지퍼 여밈\r\n· 심라인 포켓\r\n· 시어링 전체 안감\r\n· 실버 톤 하드웨어',164500.00,42,'2025-04-26 02:26:20','2025-04-26 02:26:20'),(70,7,'브라운 소프트 나파 가죽 재킷','나파 가죽 재킷. 오버사이즈.\r\n\r\n· 스프레드 칼라\r\n· 지퍼 여밈, 스냅 버튼 플래킷\r\n· 플랩 포켓\r\n· 신축성 있는 밑단\r\n· 드롭 숄더\r\n· 조절 가능한 스냅 버튼 소맷단\r\n· 내부에 웰트 포켓\r\n· 트윌 전체 안감',370500.00,43,'2025-04-26 02:26:49','2025-04-26 02:26:49'),(71,7,'그레이 폴카 도트 프린트 오버사이즈 재킷','코튼 트윌 오버사이즈 재킷. 폴카 도트 패턴 프린트.\r\n\r\n· 스프레드 칼라\r\n· 칼라에 스냅 버튼 여밈\r\n· 겉으로 드러나지 않는 지퍼 여밈, 스냅 버튼 플래킷\r\n· 겉으로 드러나지 않는 지퍼 포켓\r\n· 드롭 숄더\r\n· 소맷단에 스냅 버튼 탭\r\n· 내부에 플랩 포켓\r\n· 태피터 전체 안감\r\n· 로고를 새긴 실버 톤 하드웨어',260000.00,12,'2025-04-26 02:27:15','2025-04-26 02:27:15'),(72,7,'블랙 라이트 벨트 코트','가벼운 코팅 코튼 코트.\r\n\r\n· 발수 기능\r\n· 스프레드 칼라\r\n· 겉으로 드러나지 않는 스냅 버튼 여밈\r\n· 벨트 고리 및 탈부착 가능한 버클 벨트\r\n· 웰트 포켓\r\n· 래글런 소매\r\n· 뒤트임\r\n· 안감 없음',168000.00,32,'2025-04-26 02:27:41','2025-04-26 02:27:41'),(73,7,'베이지 프랭크 재킷','바이오 워싱 코튼 캔버스 재킷.\r\n\r\n· 스프레드 칼라에 코듀로이 트리밍\r\n· 양방향 지퍼 여밈, 스냅 버튼 플래킷\r\n· 플랩 포켓\r\n· 드롭 숄더\r\n· 소매 아래에 메탈 아일렛\r\n· 포플린 전체 안감',306000.00,32,'2025-04-26 02:28:18','2025-04-26 02:28:18'),(74,7,'그레이 & 네이비 스포츠 재킷','코튼 플란넬 재킷.\r\n\r\n· 스프레드 칼라\r\n· 버튼 여밈\r\n· 플랩 포켓\r\n· 겉으로 드러나지 않는 지퍼 포켓\r\n· 칼라 뒷면에 화이트 스티치\r\n· 뒷면에 이중 뒤트임, 버튼 여밈\r\n· 내부에 패치 포켓\r\n· 캔버스 부분 안감',265500.00,15,'2025-04-26 02:28:47','2025-04-26 02:28:47'),(75,7,'카키 큐프라 코트','큐프라 및 코튼 혼방 트윌 루즈 핏 코트. 주름 잡힌 디자인.\r\n\r\n· 라운드넥 및 소맷단에 드로우스트링\r\n· 오픈형 디자인\r\n· 패치 포켓\r\n· 요크 소매\r\n· 안감 없음',114000.00,16,'2025-04-26 02:29:15','2025-04-26 02:29:15'),(76,7,'블루 리본 칼라 셔츠','OEKO-TEX® 인증 리사이클 코튼 혼방 플란넬 셔츠. 페이딩 워싱.\r\n\r\n· 라운드넥에 연장된 트리밍, 묶을 수 있는 디자인\r\n· 버튼 여밈\r\n· 배럴 소맷단에 트임 및 플리츠',60500.00,25,'2025-04-26 02:29:40','2025-04-26 02:29:40'),(77,7,'블루 박시 데님 재킷','가먼트다잉한 논스트레치 데님 재킷.\r\n\r\n· 스프레드 칼라\r\n· 버튼 여밈\r\n· 가슴에 웰트 포켓\r\n· 플랩 포켓\r\n· 소맷단에 버튼 여밈\r\n· 뒷면 밑단에 조절 가능한 버튼 탭',83500.00,14,'2025-04-26 02:30:10','2025-04-26 02:30:10');
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'ADMIN'),(2,'USER');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `nickname` varchar(50) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `role_id` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `fk_users_roles` (`role_id`),
  CONSTRAINT `fk_users_roles` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin@example.com','scrypt:32768:8:1$TXIksKAQ6LgvkFag$3046b2a113bdf5751ee892d4b6f026db09d0d7397aab5e602f67fb6c65d604ddb043b76497c6333111cbf74549e25a6f4b7581ed1aa6b05bf096fd8e00971bfc','Admin_1','01000000000',1,'2025-04-18 07:27:22','2025-04-25 07:24:29'),(12,'hong1235@gmail.com','scrypt:32768:8:1$pT7Zb1YXFgXCj4vH$261354e6ece58a97e71b033a635c885958834bdcac666114e74ea31095540c42b108c284dc03957e4bfaff6688d6df3c8e8aa417333e2b48bdf30b61476a3213','hong1','01000000000',2,'2025-04-18 07:50:21','2025-04-25 11:11:22'),(13,'choi1234@gmail.com','scrypt:32768:8:1$ITpYnrAjuQ5CmKdm$ca2f0aa06cbfb51a7f560b4486132bb31f67536311d27902fdb8bae86ebfa58afd70db4c9660bac0d3d11db925b6b1545a68ce10ff72966ba5dc18cd26f8ccd9','onejin','01012345678',2,'2025-04-25 02:11:25','2025-04-25 02:11:25'),(14,'won@gmail.com','scrypt:32768:8:1$C69VPFmDndINZhCS$7d9ebdaba7dd6d10d75b6852fad717eae69cec8c548dbfc6867e4099001e3aeb422a2c4869c8f7d1278bde937815cb28bc7cf69a695a4c9ada8c0b6bf7e400bb','won','01000000000',2,'2025-04-25 10:59:08','2025-04-25 10:59:08'),(15,'won1@gmail.com','scrypt:32768:8:1$fWijR1LPuygQnrLD$97c18c13fa964cfcc21f44270f976d66c7212e8d4efa6fafa3dedc6d61212b6f9fd738c1b5c95b60bf1a5a57224cccb351e531e8f4bf559aa4450e4d395ead39','won','01000000000',2,'2025-04-25 10:59:59','2025-04-25 11:02:00'),(16,'won2@gmail.com','scrypt:32768:8:1$LWeXSJDUCTuk2y9w$185e758766b8027be52228d8048c336f73d2c13d826ed95e6e0c1dac02a56af6c1160e897816bc119eb1afab25906d6fb8771db4e035bb1eadcfd1e729b8f245','wonjin','01012345678',2,'2025-04-25 11:02:19','2025-04-26 04:04:56'),(17,'donghyeok7312@naver.com','scrypt:32768:8:1$qE8TkyCwUYmnAzcd$9ea9e6952c00f4c985e28dd1dabb0808755bb763d7ef4e98dfc1702cb814ca22ae7a0bea468a64ef138c443cb78c42a6e46ccac66823f5ac5781f0425eba0b05','donghyeok','01012345678',2,'2025-04-26 00:28:40','2025-04-26 00:28:40'),(18,'handonghyeok7312@gmail.com','scrypt:32768:8:1$MjjP8RJv8aj4woWR$3c036edb7067a1f77a0ff2f53e57c95df4ab33331cac2a77a0633de5a891b9295bf1ab2ba202fe0fe313401c6164e59890a34886a68c3da13d5bc82d230a7e33','테스트1','123456',2,'2025-04-26 00:34:43','2025-04-26 00:34:43'),(19,'songjae@song.com','scrypt:32768:8:1$stm5Y8jl719foW0j$28bb0832649ce41391888bfa01bce260aaf147c433261fb359822513b9b8e7405c1d18933282052fd155dc6076f9a21d97854e221658dd847901e61aa0706d13','songjae44','01012345678',2,'2025-04-26 08:02:28','2025-04-26 08:02:28');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-29 16:45:01
