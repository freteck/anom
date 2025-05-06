import React from 'react';
import { MailOutlined } from '@ant-design/icons';
import { Input, Button, Table, Divider, Space} from 'antd';
import { Geist, Geist_Mono } from "next/font/google";
import Header from "./components/header";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export function SpacedDivider(props: {className?: string}) {
  return <Divider className={`!my-10 !min-w-[0px] !w-[400px] max-w-[50vw] bg-[#00000022]`}/>
}

const columns = [
  {
    title: 'Time Identified',
    dataIndex: 'time',
    key: 'time',
  },
  {
    title: 'Type',
    dataIndex: 'type',
    key: 'type',
  }
]


export default function Home() {
  return (
    <div className={`${geistSans.className} ${geistMono.className} font-[family-name:var(--font-geist-sans)]`}>
      <Header/>
      <main className="w-screen relative flex min-h-[100dvh] flex-col overflow-hidden items-center bg-background px-5 md:py-[100px] py-[100px] bg-[linear-gradient(to_right,#80808022_1px,transparent_1px),linear-gradient(to_bottom,#80808022_1px,transparent_1px)] bg-[size:70px_70px]">
        <div className="text-4xl font-bold max-w-3/4 text-center ">
          The High-Velocity, High-Volume Anomalous Request Detector
        </div>
        <div className="w-1/2 flex flex-col items-center">
          <div className="text-xl mt-5">Currently analyzing requests from:</div>
          <div className="bg-white border-2 rounded-md w-full text-center py-2 text-2xl font-[Courier] mt-5">access.log</div>
          <SpacedDivider/>
          <div className="text-xl mb-2">Want live updates on anomalies?</div>
          <div className='flex justify-between items-center w-full'>
            <Input className="mr-2" size="large" prefix={<MailOutlined/>}/>
            <Button size="large" type="primary">Subscribe</Button>
          </div>
        </div>
        <SpacedDivider/>
        <div className='w-3/4 flex flex-col items-center'>
          <div className="text-3xl font-bold mb-5">
            Live Anomaly Report
          </div>
          <Table className="w-3/4 border-2 rounded-md" columns={columns}>
          </Table>

        </div>

      </main>
    </div>
  );
}
