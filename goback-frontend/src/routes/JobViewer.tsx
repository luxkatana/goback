import { useContext, useEffect, useState } from "react";
import toast from "react-hot-toast";
import { useLocation, useNavigate } from "react-router-dom";
import { AuthContext, FetchJobInfo } from "../utils/AuthContext";
import { Heading, Text, VStack } from "@chakra-ui/react";

type JobInfo = {
	created_at: string,
	status: string,
	job_id: number
}

export default function JobViewer() {
	const location = useLocation();
	const navigate = useNavigate();
	const [job_info, setjobinfo] = useState<JobInfo | null>(null);
	const authcontext = useContext(AuthContext);
	useEffect(() => {
		const search = new URLSearchParams(location.search);
		const job_id_to_search: number = parseInt(search.get("job_id")!); // will return NaN if incorrect number
		async function fetchinfo() {
			try {
				const response: JobInfo = await FetchJobInfo(job_id_to_search, authcontext);
				if (isMounted) setjobinfo(response);
			} catch (_: any) {
				toast.error(`Whoops, job not found!`);
				navigate("/dashboard");
				return clearEffect
			}

		}
		fetchinfo();
		const fetch_interval = setInterval(fetchinfo, 2000);
		function clearEffect() {
			isMounted = false;
			clearInterval(fetch_interval);
		}
		let isMounted = true;
		if (isNaN(job_id_to_search)) {
			toast.error("Whoopsie, just accessed an inaccessible page (missing job id)");
			navigate("/dashboard");
			return clearEffect
		}
		return clearEffect
	}, [location.search, navigate, authcontext]);
	return <><VStack>
		{job_info && <>
			<Heading fontSize="6xl" marginTop={10}>
				Job Viewer - {job_info.job_id}
			</Heading>
			<Text fontSize="4xl" marginTop={10}>{job_info.status}</Text>
			<Text fontSize="4xl">created at: {new Date(job_info.created_at).toLocaleTimeString()}</Text>
		</>}

	</VStack>
	</>
}
