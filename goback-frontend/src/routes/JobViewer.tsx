import { useContext, useEffect, useRef, useState } from "react";
import toast from "react-hot-toast";
import { useLocation, useNavigate } from "react-router-dom";
import { AuthContext, FetchJobInfo } from "../utils/AuthContext";
import type { Job } from "../types/Job";
import { Box, Heading, List, Text, VStack, Link } from "@chakra-ui/react";
import { CiCircleInfo } from "react-icons/ci";
import { IoIosCheckmarkCircle, IoIosWarning } from "react-icons/io";
import { BiSolidCommentError } from "react-icons/bi";
import Navbar from "../components/Navbar";



enum StatusTypes {
	SUCCESS = 0,
	INFO = 1,
	ERROR = 2,
	FAILED = 3


}
export default function JobViewer() {
	const location = useLocation();
	const navigate = useNavigate();

	const [job_info, setjobinfo] = useState<Job | null>(null);
	const shouldRequestData = useRef(true);
	const [currentstate, setcurrentstate] = useState(-1); // 0 or 3
	useEffect(() => {
		if (job_info == null || job_info?.status_messages.length == 0) return;
		const last_element = job_info.status_messages[job_info.status_messages.length - 1];
		if (last_element.status_type == StatusTypes.SUCCESS || last_element.status_type == StatusTypes.FAILED) {
			setcurrentstate(last_element.status_type);
			shouldRequestData.current = false;
		}
	}), [job_info?.status_messages];
	const authcontext = useContext(AuthContext);
	useEffect(() => {
		const search = new URLSearchParams(location.search);
		const job_id_to_search: number = parseInt(search.get("job_id")!); // will return NaN if incorrect number
		async function fetchinfo() {
			if (shouldRequestData.current == false) { return }
			try {
				const response: Job = await FetchJobInfo(job_id_to_search, authcontext);
				if (isMounted) setjobinfo(response);
			} catch (_: any) {
				toast.error(`Whoops, job not found!`);
				navigate("/dashboard");
				return clearEffect
			}

		}
		if (isNaN(job_id_to_search)) {
			toast.error("Whoopsie, just accessed an inaccessible page (missing job id)");
			navigate("/dashboard");
			return clearEffect
		}
		fetchinfo();
		const fetch_interval = setInterval(fetchinfo, 2000);
		function clearEffect() {
			isMounted = false;
			clearInterval(fetch_interval);
		}
		let isMounted = true;
		return clearEffect
	}, [location.search, navigate, authcontext]);
	return <>
		<Navbar />
		<VStack>
			{job_info && <>
				<Heading fontSize="6xl" marginTop={10}>
					Job Viewer - {job_info.job_id} {currentstate == -1 && <>- Working on...</>}
				</Heading>
				<Text fontSize="4xl" marginTop="20px">created at: {new Date(job_info.created_at).toLocaleTimeString()}</Text>
				<Box border="3px" borderStyle="solid" boxSize="1xl" padding="20px" marginTop="20px">
					<Text fontSize="4xl" textAlign="center">Status of job</Text>
					<List.Root fontSize="2xl" padding="50px">
						{job_info.status_messages.map((job, index) =>
							<List.Item key={index}>
								{job.status_type == StatusTypes.SUCCESS && <List.Indicator asChild color="green.300"><IoIosCheckmarkCircle /></List.Indicator>}
								{job.status_type == StatusTypes.INFO && <List.Indicator asChild color="blue.300"><CiCircleInfo /></List.Indicator>}
								{job.status_type == StatusTypes.ERROR && <List.Indicator asChild color="yellow.300"><IoIosWarning /></List.Indicator>}
								{job.status_type == StatusTypes.FAILED && <List.Indicator asChild color="red.300"><BiSolidCommentError /></List.Indicator>}

								{job.status_type != StatusTypes.SUCCESS && job.message}
								{job.status_type == StatusTypes.SUCCESS && <Link
									href={`/media/${job.message}`}
									color="green.200"
									_hover={{ color: "gray.50" }}
								>{job.message} (click to view)</Link>}

							</List.Item>)}
					</List.Root>
				</Box>
				{currentstate == 0 && <Text color="green.300" fontSize="3xl">🎉Finished</Text>}
			</>}

		</VStack >
	</>
}
