import { Link } from "react-router-dom";

export interface Candidate {
  id: number;
  nik: string;
  full_name: string;
  status: string;
  birth_date: string; // format "YYYY-MM-DD" atau bisa berupa format tanggal lain
  department: string;
  location: string;
  division: string;
  position: string;
  education_major: string;
  education_institute: string;
  company_history: string;
  position_history: string;
}

export function Card({ data }: { data: Candidate }) {
  return (
    <div className="w-full border rounded-2xl border-gray-200 bg-white p-4 shadow-sm mb-4">
      {/* Header Profil */}
      <div className="flex items-start">
        <img
          className="h-20 w-20 object-cover"
          src="/assets/profile.png"
          alt="Profile"
        />
        <div className="flex flex-col ml-4">
          <div className="text-lg text-blue-600 font-semibold">
            {data.full_name}
          </div>
          <div className="flex text-sm">
            <div className="w-24 font-semibold">Departemen</div>
            <div className="mr-2">:</div>
            <div>{data.department}</div>
          </div>
          <div className="flex text-sm">
            <div className="w-24 font-semibold">Lokasi</div>
            <div className="mr-2">:</div>
            <div>{data.location}</div>
          </div>
        </div>
      </div>

      {/* Detail Tambahan */}
      <div className="mt-4 text-sm text-gray-700 space-y-1">
        <div className="flex">
          <div className="w-40 font-semibold">Status</div>
          <div className="w-2">:</div>
          <div>{data.status}</div>
        </div>
        <div className="flex">
          <div className="w-40 font-semibold">Tanggal Lahir</div>
          <div className="w-2">:</div>
          <div>{data.birth_date.replace(' 00:00:00 GMT', '')}</div>
        </div>
        <div className="flex">
          <div className="w-40 font-semibold">Divisi</div>
          <div className="w-2">:</div>
          <div>{data.division}</div>
        </div>
        <div className="flex">
          <div className="w-40 font-semibold">Posisi</div>
          <div className="w-2">:</div>
          <div>{data.position}</div>
        </div>
        <div className="flex">
          <div className="w-40 font-semibold">Pendidikan</div>
          <div className="w-2">:</div>
          <div>
            {data.education_details}
          </div>
        </div>
        <div className="flex">
          <div className="w-40 font-semibold">Skill & certificate</div>
          <div className="w-2">:</div>
          <div>
            {data.certificates}
          </div>
        </div>
        <div className="flex">
          <div className="w-40 font-semibold">Riwayat Pekerjaan</div>
          <div className="w-2">:</div>
          <div>{data.position_history}</div>
        </div>
        <div className="flex">
          <div className="w-40 font-semibold">Riwayat Perusahaan</div>
          <div className="w-2">:</div>
          <div>{data.company_history}</div>
        </div>
        <br></br>
        <div className="flex">
          {/* <div className="w-40 font-semibold">Alasan</div> */}
          {/* <div className="w-2">:</div> */}
          <div>{data.alasan}</div>
        </div>
      </div>

      {/* Tombol Detail */}
      <Link to={`/admin/save-to-cart/${data.id}`} target="_blank">
        <button className="mt-3 px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600">
          Save to Cart
        </button>
      </Link>
    </div>
  );
}
