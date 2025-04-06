-- MySQL dump 10.13  Distrib 8.0.34, for Win64 (x86_64)
--
-- Host: localhost    Database: voters
-- ------------------------------------------------------
-- Server version	8.0.35

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `candidates`
--

DROP TABLE IF EXISTS `candidates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `candidates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `party` varchar(255) NOT NULL,
  `symbol` varchar(255) DEFAULT NULL,
  `position` varchar(255) NOT NULL,
  `state` varchar(255) NOT NULL,
  `constituency` varchar(255) NOT NULL,
  `bio` text,
  `age` int DEFAULT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `contact_info` varchar(255) DEFAULT NULL,
  `votes` int DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `candidates`
--

LOCK TABLES `candidates` WRITE;
/*!40000 ALTER TABLE `candidates` DISABLE KEYS */;
INSERT INTO `candidates` VALUES (1,'Narendra Sharma','Bharatiya Janata Party (BJP)','bjp.png','Member of Parliament','Uttar Pradesh','Varanasi','Experienced leader focused on national development.',58,'Male','narendra.sharma@example.com',0,'2025-04-01 14:31:12','2025-04-01 14:31:12'),(2,'Rahul Verma','Indian National Congress (INC)','congress.png','Member of Parliament','Maharashtra','Mumbai South','Young leader advocating for youth empowerment.',45,'Male','rahul.verma@example.com',0,'2025-04-01 14:31:12','2025-04-01 14:31:12'),(3,'Anjali Reddy','Telangana Rashtra Samithi (TRS)','trs.png','Member of Legislative Assembly','Telangana','Hyderabad','Dedicated to regional development and welfare schemes.',42,'Female','anjali.reddy@example.com',0,'2025-04-01 14:31:12','2025-04-01 14:31:12'),(4,'Priya Singh','Aam Aadmi Party (AAP)','aap.png','Member of Legislative Assembly','Delhi','New Delhi','Passionate about education and healthcare reforms.',38,'Female','priya.singh@example.com',0,'2025-04-01 14:31:12','2025-04-01 14:31:12'),(5,'Amit Patil','Shiv Sena','shiv_sena.png','Member of Parliament','Maharashtra','Pune','Focused on urban infrastructure and safety.',50,'Male','amit.patil@example.com',0,'2025-04-01 14:31:12','2025-04-01 14:31:12'),(6,'Deepak Yadav','Samajwadi Party (SP)','sp.png','Member of Legislative Assembly','Uttar Pradesh','Lucknow','Committed to rural development and employment.',47,'Male','deepak.yadav@example.com',0,'2025-04-01 14:31:12','2025-04-01 14:31:12'),(7,'Kavita Nair','Communist Party of India (CPI)','cpi.png','Member of Parliament','Kerala','Thiruvananthapuram','Advocate for labor rights and environmental issues.',54,'Female','kavita.nair@example.com',0,'2025-04-01 14:31:12','2025-04-01 14:31:12'),(8,'Manoj Gupta','Bahujan Samaj Party (BSP)','bsp.png','Member of Parliament','Madhya Pradesh','Bhopal','Working towards social justice and upliftment.',49,'Male','manoj.gupta@example.com',0,'2025-04-01 14:31:12','2025-04-01 14:31:12'),(9,'Ramesh Iyer','Dravida Munnetra Kazhagam (DMK)','dmk.png','Member of Legislative Assembly','Tamil Nadu','Chennai Central','Focused on digital transformation and IT industry.',41,'Male','ramesh.iyer@example.com',0,'2025-04-01 14:31:12','2025-04-01 14:31:12'),(10,'Meera Das','Trinamool Congress (TMC)','tmc.png','Member of Parliament','West Bengal','Kolkata North','Dedicated to women empowerment and public welfare.',39,'Female','meera.das@example.com',0,'2025-04-01 14:31:12','2025-04-01 14:31:12');
/*!40000 ALTER TABLE `candidates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `voterId` varchar(20) NOT NULL,
  `name` varchar(255) NOT NULL,
  `fingerprint_template` longblob NOT NULL,
  `phone_number` varchar(15) NOT NULL,
  `photo` varchar(255) DEFAULT NULL,
  `address` text NOT NULL,
  `aadhaar` varchar(12) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `voterId` (`voterId`),
  UNIQUE KEY `phone_number` (`phone_number`),
  UNIQUE KEY `aadhaar` (`aadhaar`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'VOTER12345','shyam',_binary '¡ÿ\ë\êõLe=l0:û]@½•š¡Û‰rµ>™õ\äš\åV®œƒ}|¨ƒ(Žl\å][9.^\Ï\Í\ì\Å4ZUME—!dn¡2\ë]¨x3xÈ¿F+\Z/yK4{Eù?\Ü)@\ê\ï\ã\Ò\Ñ,À{+7·RŽ7!Ú›\É&\Î;•r;\Üg)^uþ$—\ç{rOD‚Š\áM!¿Ð“\ÔQ\æC­A’š\Ý,p¶Q_C\Þ!º±²†rú‰™c-~\0»?#Ž.NŽ¤/)¸u¼\ÌýdO”¸Ý´q\Þn¼a%\Õø~ô¥O\nÏ‡„ˆˆC\èö;$©«Kx+\àý¤n’C_’8z«@¿˜\Í\Ìa«\Å>.-Dªž\Ød\×\ë¦\ã¡-@“	ö\å\Í\ìCÃŸb\ÛR·¶\Å\ÄnQ•\ïŸ?r}^\áö\ÎP­½ˆ}F±³ñJ|p\ØCY:\Öd¿;Á\ÛÅ™‚\å\í\È\Ý?9v SyJ\Ð\í/L\Ìi%ñ`$¥»´\Æz\åEg\â]Bc;´n>x‚Jx›Z¶A¸Q/yù¨ƒdº\î\'µuü\ÓjU-\ÝZsS\ß\Åøu\ï\é\Ñ\ÏRŠç†ž\Ó\áE k{Fðv¤«½£(š‰&“kª8\ÌÒ½UÉ¨ðò\âr|ª#we\Þ];œ¥\ëÈ¾§bôFµ‚¹¡‘\ë³`ÒŒ´š˜n±\È|Ÿ\Û¢aù¾°:>k´\é)Œ‡b`§\ÄûO¬õu˜kð•yd\Äç§²ùÂ»','9392584801','1.jpg','SF- 304 , teja colony, Isnapur','123456789101');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `voters`
--

DROP TABLE IF EXISTS `voters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `voters` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) DEFAULT NULL,
  `phone_number` varchar(15) DEFAULT NULL,
  `aadhaar_number` varchar(20) DEFAULT NULL,
  `fingerprint_id` int DEFAULT NULL,
  `fingerprint_image` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `fingerprint_id` (`fingerprint_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `voters`
--

LOCK TABLES `voters` WRITE;
/*!40000 ALTER TABLE `voters` DISABLE KEYS */;
/*!40000 ALTER TABLE `voters` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-02 14:31:59
