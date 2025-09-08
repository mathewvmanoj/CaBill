import React, { useState, useRef } from "react";
import * as XLSX from "xlsx";
import Sidebar from "./Sidebar";
import {
  Box,
  Button,
  Container,
  Heading,
  Select,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Flex,
  Text,
  ButtonGroup,
  useColorModeValue,
} from "@chakra-ui/react";

function Schedule() {
  const [filters, setFilters] = useState({
    group: "",
    subject: "",
    room: "",
    instructor: "",
  });

  const [schedules, setSchedules] = useState([]);
  const fileInputRef = useRef(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(20);

  const handleFilterChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const handleImportClick = () => {
    fileInputRef.current.click();
  };

  const handleRowsPerPageChange = (e) => {
    setItemsPerPage(Number(e.target.value));
    setCurrentPage(1);
  };

  const formatTime = (timeStr) => {
    if (!timeStr) return "";

    try {
      // For Excel's decimal time format
      if (typeof timeStr === "number" || !isNaN(timeStr)) {
        const decimalTime = parseFloat(timeStr);
        const hours = Math.floor(decimalTime * 24);
        const minutes = Math.round((decimalTime * 24 - hours) * 60);

        const period = hours >= 12 ? "PM" : "AM";
        let displayHours = hours % 12;
        if (displayHours === 0) displayHours = 12;

        return `${displayHours}:${minutes
          .toString()
          .padStart(2, "0")} ${period}`;
      }

      // For string time format (e.g., "8:00 AM")
      if (typeof timeStr === "string") {
        // If it's already in the correct format, return as is
        if (timeStr.includes("AM") || timeStr.includes("PM")) {
          return timeStr;
        }

        // Parse HH:mm format
        const [hours, minutes] = timeStr
          .split(":")
          .map((num) => parseInt(num, 10));
        const period = hours >= 12 ? "PM" : "AM";
        let displayHours = hours % 12;
        if (displayHours === 0) displayHours = 12;

        return `${displayHours}:${minutes
          .toString()
          .padStart(2, "0")} ${period}`;
      }
    } catch (error) {
      console.error("Error formatting time:", error);
      return timeStr; // Return original value if formatting fails
    }

    return timeStr;
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];

    if (file) {
      const reader = new FileReader();
      reader.readAsBinaryString(file);

      reader.onload = (e) => {
        const data = e.target.result;
        const workbook = XLSX.read(data, { type: "binary" });
        const sheetName = workbook.SheetNames[0];
        const sheet = workbook.Sheets[sheetName];

        // Parse Excel data with raw values
        const parsedData = XLSX.utils.sheet_to_json(sheet, {
          raw: true,
          dateNF: "HH:mm",
        });

        const formattedData = parsedData.map((row, index) => {
          console.log("Raw Start Time:", row["Start Time"]);
          console.log("Raw End Time:", row["End Time"]);

          return {
            id: index + 1,
            subject: row["Subject"] || "",
            group: row["Group"] || "",
            startDate: row["Start Date"] || "",
            endDate: row["End Date"] || "",
            startTime: formatTime(row["Start Time"]),
            endTime: formatTime(row["End Time"]),
            days: row["Days of the Week"] || "",
            room: row["Room"] ? String(row["Room"]) : "",
            instructor: row["Instructor"] || "",
          };
        });

        setSchedules(formattedData);
      };
    }
  };

  const filterValues = {
    groups: [...new Set(schedules.map((s) => s.group))],
    subjects: [...new Set(schedules.map((s) => s.subject))],
    room: [...new Set(schedules.map((s) => s.room))],
    instructor: [...new Set(schedules.map((s) => s.instructor))],
  };

  const filteredSchedules = schedules.filter((schedule) => {
    return (
      (filters.group === "" || schedule.group === filters.group) &&
      (filters.subject === "" || schedule.subject === filters.subject) &&
      (filters.room === "" || schedule.room === filters.room) &&
      (filters.instructor === "" || schedule.instructor === filters.instructor)
    );
  });

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = filteredSchedules.slice(
    indexOfFirstItem,
    indexOfLastItem
  );
  const totalPages = Math.ceil(filteredSchedules.length / itemsPerPage);

  const Pagination = () => {
    const activeStyle = {
      bg: useColorModeValue("blue.500", "blue.300"),
      color: "white",
    };

    const normalStyle = {
      bg: useColorModeValue("gray.100", "gray.700"),
      color: useColorModeValue("gray.700", "gray.200"),
      _hover: {
        bg: useColorModeValue("gray.200", "gray.600"),
      },
    };

    const getPageNumbers = () => {
      const pages = [];
      if (totalPages <= 7) {
        for (let i = 1; i <= totalPages; i++) {
          pages.push(i);
        }
      } else {
        if (currentPage <= 4) {
          for (let i = 1; i <= 5; i++) {
            pages.push(i);
          }
          pages.push("...");
          pages.push(totalPages);
        } else if (currentPage >= totalPages - 3) {
          pages.push(1);
          pages.push("...");
          for (let i = totalPages - 4; i <= totalPages; i++) {
            pages.push(i);
          }
        } else {
          pages.push(1);
          pages.push("...");
          for (let i = currentPage - 1; i <= currentPage + 1; i++) {
            pages.push(i);
          }
          pages.push("...");
          pages.push(totalPages);
        }
      }
      return pages;
    };

    return (
      <Box>
        <Flex justify="space-between" align="center" mb={4}>
          <Flex align="center" gap={4}>
            <Flex align="center" gap={2}>
              <Text>Show</Text>
              <Select
                value={itemsPerPage}
                onChange={handleRowsPerPageChange}
                w="80px"
                size="sm"
              >
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </Select>
              <Text>entries</Text>
            </Flex>
            <Text>
              Showing {indexOfFirstItem + 1} to{" "}
              {Math.min(indexOfLastItem, filteredSchedules.length)} of{" "}
              {filteredSchedules.length} entries
            </Text>
          </Flex>
        </Flex>

        <Flex justify="center" align="center">
          <ButtonGroup isAttached variant="outline" spacing={0}>
            <Button
              onClick={() => setCurrentPage(1)}
              isDisabled={currentPage === 1}
              {...normalStyle}
            >
              First
            </Button>
            <Button
              onClick={() => setCurrentPage(currentPage - 1)}
              isDisabled={currentPage === 1}
              {...normalStyle}
            >
              Previous
            </Button>

            {getPageNumbers().map((pageNum, index) => (
              <Button
                key={index}
                onClick={() =>
                  pageNum !== "..." ? setCurrentPage(pageNum) : undefined
                }
                {...(pageNum === currentPage ? activeStyle : normalStyle)}
                isDisabled={pageNum === "..."}
              >
                {pageNum}
              </Button>
            ))}

            <Button
              onClick={() => setCurrentPage(currentPage + 1)}
              isDisabled={currentPage === totalPages}
              {...normalStyle}
            >
              Next
            </Button>
            <Button
              onClick={() => setCurrentPage(totalPages)}
              isDisabled={currentPage === totalPages}
              {...normalStyle}
            >
              Last
            </Button>
          </ButtonGroup>
        </Flex>
      </Box>
    );
  };

  return (
    <Box display={"flex"}>
      <Sidebar />
      <Container w={"80%"} maxW={"80%"}>
        <Box display={"flex"} justifyContent={"space-between"} ml={"80px"}>
          <Heading ml={"100px"}>Good Morning Finance Team</Heading>
          <Box mr={"4%"}>
            <input
              type="file"
              accept=".xlsx, .xls"
              ref={fileInputRef}
              onChange={handleFileUpload}
              style={{ display: "none" }}
            />
            <Button
              m={2}
              bg={"blue.600"}
              color="white"
              onClick={handleImportClick}
            >
              IMPORT
            </Button>
            <Button m={2} bg={"red.600"} color="white">
              EXPORT
            </Button>
          </Box>
        </Box>

        <Box display={"flex"} gap={4} my={4}>
          <Select
            name="group"
            value={filters.group}
            onChange={handleFilterChange}
            placeholder="Select Group"
            w="250px"
          >
            {filterValues.groups.map((group) => (
              <option key={group} value={group}>
                {group}
              </option>
            ))}
          </Select>

          <Select
            name="subject"
            value={filters.subject}
            onChange={handleFilterChange}
            placeholder="Select Subject"
            w="250px"
          >
            {filterValues.subjects.map((subject) => (
              <option key={subject} value={subject}>
                {subject}
              </option>
            ))}
          </Select>

          <Select
            name="room"
            value={filters.room}
            onChange={handleFilterChange}
            placeholder="Select Room"
            w="250px"
          >
            {filterValues.room.map((room) => (
              <option key={room} value={room}>
                {room}
              </option>
            ))}
          </Select>

          <Select
            name="instructor"
            value={filters.instructor}
            onChange={handleFilterChange}
            placeholder="Select Instructor"
            w="250px"
          >
            {filterValues.instructor.map((instructor) => (
              <option key={instructor} value={instructor}>
                {instructor}
              </option>
            ))}
          </Select>
        </Box>

        <Box>
          <Table variant="striped" colorScheme="gray">
            <Thead>
              <Tr>
                <Th>Subject</Th>
                <Th>Group</Th>
                <Th>Start Date</Th>
                <Th>End Date</Th>
                <Th>Start Time</Th>
                <Th>End Time</Th>
                <Th>Days</Th>
                <Th>Room</Th>
                <Th>Instructor</Th>
              </Tr>
            </Thead>
            <Tbody>
              {filteredSchedules.length > 0 ? (
                currentItems.map((schedule) => (
                  <Tr key={schedule.id}>
                    <Td>{schedule.subject}</Td>
                    <Td>{schedule.group}</Td>
                    <Td>{schedule.startDate}</Td>
                    <Td>{schedule.endDate}</Td>
                    <Td>{schedule.startTime}</Td>
                    <Td>{schedule.endTime}</Td>
                    <Td>{schedule.days}</Td>
                    <Td>{schedule.room}</Td>
                    <Td>{schedule.instructor}</Td>
                  </Tr>
                ))
              ) : (
                <Tr>
                  <Td colSpan="9" textAlign="center">
                    No schedules found.
                  </Td>
                </Tr>
              )}
            </Tbody>
          </Table>
          {filteredSchedules.length > 0 && <Pagination />}
        </Box>
      </Container>
    </Box>
  );
}

export default Schedule;
