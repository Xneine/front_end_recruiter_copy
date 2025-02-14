-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Jan 30, 2025 at 02:20 AM
-- Server version: 8.0.30
-- PHP Version: 8.3.7

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `markovkaryawandb`
--

-- --------------------------------------------------------

--
-- Table structure for table `employee`
--

CREATE TABLE `employee` (
  `id` bigint NOT NULL,
  `nik` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `full_name` varchar(255) NOT NULL,
  `status` enum('Aktif','Tidak Aktif') NOT NULL,
  `birth_date` date NOT NULL,
  `department` varchar(255) NOT NULL,
  `location` varchar(255) NOT NULL,
  `division` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `position` varchar(255) NOT NULL,
  `education_major` varchar(255) NOT NULL,
  `education_institute` varchar(255) NOT NULL,
  `company_history` varchar(255) NOT NULL,
  `position_history` varchar(255) NOT NULL,
  `session` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT NULL,
  `otp_code` varchar(255) NOT NULL,
  `otp_expiration` varchar(255) NOT NULL,
  `last_activity` timestamp NOT NULL,
  `session_exp` timestamp NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `employee`
--

INSERT INTO `employee` (`id`, `nik`, `email`, `password`, `full_name`, `status`, `birth_date`, `department`, `location`, `division`, `position`, `education_major`, `education_institute`, `company_history`, `position_history`, `session`, `created_at`, `updated_at`, `otp_code`, `otp_expiration`, `last_activity`, `session_exp`) VALUES
(1, '9939f053-1c74-46f9-a038-aa6486dad5da', 'pperkins@example.org', 'hashed_password', 'Vanessa Johnson', 'Aktif', '1985-05-28', 'Sales', 'Ellisland', 'stay', 'Fast food restaurant manager', 'real', 'Matthews-Howe', 'Reyes-Avery', 'Sales professional, IT', '4cf5c15a-262c-4a8f-a41f-1eaaea315856', '2025-01-28 08:02:23', NULL, '206931', '2025-01-28 15:07:23', '2025-01-01 09:17:39', '2025-02-04 08:02:23'),
(2, '47a9ae52-04d2-442d-a845-648111cc15a4', 'ccarey@example.net', 'hashed_password', 'Samantha House', 'Aktif', '1986-04-05', 'Human Resources', 'Hortonview', 'charge', 'Scientist, research (life sciences)', 'mean', 'Vargas PLC', 'Davis-Smith', 'Microbiologist', '2bbb5d59-431e-40b5-b9f3-f193af525318', '2025-01-28 08:02:23', NULL, '67190', '2025-01-28 15:07:23', '2025-01-23 11:15:44', '2025-02-04 08:02:23'),
(3, '71208e58-25ce-4cc3-b94f-bc9c3e56e49c', 'kjohnson@example.net', 'hashed_password', 'Charles Watson', 'Aktif', '1982-11-18', 'Marketing', 'North Miranda', 'only', 'Media buyer', 'learn', 'Robinson, Lawrence and Combs', 'Griffin Ltd', 'Outdoor activities/education manager', '6b3a5702-47f4-4b24-8cb0-18721e8306b0', '2025-01-28 08:02:23', NULL, '55781', '2025-01-28 15:07:23', '2025-01-01 09:39:45', '2025-02-04 08:02:23'),
(4, '6ac29942-581c-462b-aa35-ed7e414a1628', 'kelsey23@example.org', 'hashed_password', 'Jason Weaver', 'Aktif', '1965-05-13', 'Engineering', 'West Andrew', 'outside', 'Museum/gallery exhibitions officer', 'energy', 'Wilson Group', 'Price-Lee', 'Logistics and distribution manager', '65f2b22a-d382-4895-8ef4-4ee5ba44490c', '2025-01-28 08:02:23', NULL, '295030', '2025-01-28 15:07:23', '2025-01-04 21:44:57', '2025-02-04 08:02:23'),
(5, '52c7df4c-33df-4659-bcda-9dbde9f9e29e', 'michaeldixon@example.net', 'hashed_password', 'Angela Page', 'Aktif', '1991-09-12', 'IT', 'Danielville', 'dark', 'Illustrator', 'safe', 'Ramos, Hawkins and Hess', 'Espinoza, Mcdowell and Rice', 'Data scientist', '56f13e51-dad0-46a2-bff8-f5e9dbbe1afc', '2025-01-28 08:02:23', NULL, '430231', '2025-01-28 15:07:23', '2025-01-12 03:04:37', '2025-02-04 08:02:23'),
(6, '3e909a05-2b3d-4e80-a1bc-efadad3dc96c', 'jessica79@example.com', 'hashed_password', 'Brett Hatfield', 'Aktif', '1966-03-07', 'IT', 'North Robert', 'today', 'Geochemist', 'three', 'Ellis, Young and Henderson', 'Robinson LLC', 'Insurance risk surveyor', '1a9c30bf-91f2-4a7a-8356-771e2fb326c5', '2025-01-28 08:02:23', NULL, '267598', '2025-01-28 15:07:23', '2025-01-07 14:19:14', '2025-02-04 08:02:23'),
(7, '92c333f3-93fa-414d-9c29-1b5d74d85ac6', 'johnsonjoel@example.com', 'hashed_password', 'Tracey Velazquez', 'Aktif', '1982-05-12', 'IT', 'Port Hannahborough', 'wide', 'Petroleum engineer', 'class', 'Barnes, Raymond and Mullins', 'Mullen Inc', 'Materials engineer', 'daf016b6-08f5-439d-83e1-a7baa985a884', '2025-01-28 08:02:23', NULL, '39046', '2025-01-28 15:07:23', '2025-01-17 20:20:25', '2025-02-04 08:02:23'),
(8, '089d9e72-a93d-4ee6-84a5-3a8334bd2f7e', 'avaughan@example.org', 'hashed_password', 'Ashley Rice', 'Aktif', '2000-06-28', 'Human Resources', 'Masseyfort', 'little', 'Cartographer', 'personal', 'Harris, Cole and Brown', 'Contreras, Mills and Hernandez', 'Hydrogeologist', 'c9be720a-f89e-4768-851d-fe446970d3f0', '2025-01-28 08:02:23', NULL, '971413', '2025-01-28 15:07:23', '2025-01-13 15:37:49', '2025-02-04 08:02:23'),
(9, '17bdd1fb-cbfe-435b-9528-9823d75745c6', 'rallen@example.com', 'hashed_password', 'David Stafford', 'Aktif', '1973-11-30', 'Finance', 'Harrisview', 'central', 'Gaffer', 'yet', 'Sanders, Taylor and Wallace', 'Morrison, Smith and Sweeney', 'Science writer', '5e15e975-b75a-4427-990b-9c5681ecaa81', '2025-01-28 08:02:23', NULL, '786082', '2025-01-28 15:07:23', '2025-01-23 11:53:06', '2025-02-04 08:02:23'),
(10, 'facaef91-6fbb-4cea-943f-9be9268d2f0f', 'luke92@example.net', 'hashed_password', 'Samantha Evans', 'Aktif', '1966-11-14', 'Finance', 'North Ericchester', 'themselves', 'Customer service manager', 'story', 'Ellis, Murray and Smith', 'Jones-Hall', 'Industrial buyer', '2a2c7b31-ac6d-4107-838d-8129e1f342dc', '2025-01-28 08:02:23', NULL, '545943', '2025-01-28 15:07:23', '2025-01-05 05:39:00', '2025-02-04 08:02:23');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `employee`
--
ALTER TABLE `employee`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nik` (`nik`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `employee`
--
ALTER TABLE `employee`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
