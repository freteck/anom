import React, { useMemo, useState } from 'react';
import { MailOutlined } from '@ant-design/icons';
import { Input, Button, Table, Divider, Space, notification} from 'antd';
import { Geist, Geist_Mono } from "next/font/google";
import Header from "./components/header";
import { NotificationPlacement } from 'antd/es/notification/interface';

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


function isValidEmail(email: string) {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}

const Context = React.createContext({ name: 'Default' });

export default function Home() {
  const [api, contextHolder] = notification.useNotification();
  const [email, setEmail] = useState<string>("");
  const contextValue = useMemo(() => ({ name: 'Ant Design' }), []);
  
  const openNotification = (placement: NotificationPlacement) => {
    api.success({
      message: `Subscription Successful!`,
      placement,
    });
  };

  const invalidEmailNotification = (placement: NotificationPlacement) => {
    api.error({
      message: `Invalid Email Address`,
      placement,
    });
  };

  function subscribe(email: string) {
    if (!isValidEmail(email)) {
      invalidEmailNotification("bottomRight");
      return;
    }

    fetch("/api/subscribe", {
      method: "POST",
      body: JSON.stringify({
        email
      })
    });
    openNotification("bottomRight");
    setEmail("")
  }

  return (
    <Context.Provider value={contextValue}>
    {contextHolder}
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
            <Input className="mr-2" size="large" prefix={<MailOutlined/>} onChange={(e) => setEmail(e.target.value)} onPressEnter={() => subscribe(email)}/>
            <Button size="large" type="primary" onClick={() => subscribe(email)}>Subscribe</Button>
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
    </Context.Provider>
  );
}
