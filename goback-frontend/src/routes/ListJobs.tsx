import { useContext, useEffect, useState } from "react";
import { AuthContext, GetJobs } from "../utils/AuthContext";
import Navbar from "../components/Navbar";
import type { Job } from "../types/Job";
import { useNavigate, Link as RouterLink } from "react-router-dom";
import { Link, List, Spinner, Text, VStack } from "@chakra-ui/react";

export default function ListJobs() {
	const navigate = useNavigate();
	const auth_context = useContext(AuthContext);
	const [jobs, setjobs] = useState<Job[]>([] as Job[]);
	const [fetched, setfetched] = useState<boolean>(false);
	useEffect(() => {
		async function fetch_jobs() {
			const response: { success: boolean, jobs?: Job[] } = await GetJobs(auth_context)
			setfetched(true);
			if (response.success == true)
				setjobs(response.jobs!);
			else
				navigate("/home");

		}
		fetch_jobs()

	}, [auth_context]);
	jobs
	return <>
		<Navbar />
		<VStack>
			{!fetched && <><Spinner marginBottom={5} /><Text>Fetching data...</Text></>}
			{fetched && jobs.length == 0 && <Text>No jobs here, create a new archive!</Text>}
			{fetched && jobs.length > 0 && <>
				<List.Root>
					{
						jobs.map((job, idx) => {
							return <List.Item key={idx}>
								<Text fontSize="3xl">
									<Link asChild colorPalette="gray" _hover={{ color: "tan" }}>
										<RouterLink to={`/job?job_id=${job.job_id}`}>
											Job {job.job_id} - {new Date(job.created_at).toLocaleString()}
										</RouterLink>
									</Link>
								</Text>
							</List.Item>

						})

					}
				</List.Root>
			</>}


		</VStack>

	</>

}
