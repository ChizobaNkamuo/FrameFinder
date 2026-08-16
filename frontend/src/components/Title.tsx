import "./Title.css";
import { Layers2 } from "lucide-react";

interface TitleProps {
    children: string;
}

export default function Title({ children }: TitleProps) {
    return (
        <div className="title">
            <Layers2/>
            <h1>{children}</h1>
        </div>
    );
}